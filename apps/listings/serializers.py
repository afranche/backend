# Serializers for Category Model, Product Model

import warnings
from rest_framework import serializers
from .models import Category, ImageModel, Product, Characteristic, Listing, Variant, base64_image_to_file


class Base64ImageField(serializers.FileField):
    def to_internal_value (self, data) :
        data = base64_image_to_file(data)
        return super(Base64ImageField, self).to_internal_value(data)

class ImageModelSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    class Meta:
        model = ImageModel
        fields = ['id', 'image',]

class CategorySerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    class Meta:
        model = Category
        fields = '__all__'

class AtomicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name',]

class VariantSerializer(serializers.ModelSerializer):
    images = ImageModelSerializer(many=True, required=False)
    class Meta:
        model = Variant
        fields = ['id', 'name', 'images', 'description', 'stock', 'is_available']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = ImageModelSerializer(instance.images.all(), many=True, required=False).data
        return representation

class CharacteristicSerializer(serializers.ModelSerializer):
    choices = VariantSerializer(many=True, required=False)
    class Meta:
        model = Characteristic
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['choices'] = VariantSerializer(instance.choices.all(), many=True).data
        return representation
    
    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        characteristic = Characteristic.objects.create(**validated_data)
        for choice in choices_data:
            images_data = choice.pop('images', [])
            images = []
            for image_data in images_data:
                image, created = ImageModel.objects.get_or_create(**image_data)
                images.append(image)
            variant, created = Variant.objects.get_or_create(**choice)
            variant.images.set(images)
            variant.save()
            characteristic.choices.add(variant)
        return characteristic

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'manufacturer', 'price', 'weight', 'conservation', 'lang', 'description']


class AtomicListingSerializer(serializers.ModelSerializer):

    categories = AtomicCategorySerializer(many=True)
    images = ImageModelSerializer(many=True, required=False)
    name = serializers.CharField(source='product.name')
    price = serializers.FloatField(source='product.price')
    stock = serializers.IntegerField()
    is_available = serializers.BooleanField()

    class Meta:
        model = Listing
        fields = ['id',
                  'name',
                  'images',
                  'stock',
                  'is_available',
                  'price',
                  'categories']

    def to_representation(self, instance):
        """
            I don't know if it's smart, but too tired to think of something else.
            No I think it's better to have all variants in the same listing, rather than just the first one.
            I want to have something like this:
            [
                {
                "id": 1,
                "name": "Tote bag blanc avec un imprimé au choix",
                "images": [
                    "http://localhost:8000/media/listings/2021/06/01/tote-bag-blanc-avec-un-imprime-au-choix.jpg"
                ],
                "stock": 5,
                "is_available": true,
                "price": 25,
                "attr_name": "le motif que vous voulez",
                "categories": [
                    {
                    "id": 1,
                    "name": "Accessoires"
                    }
                ]
                },
                {
                "id": 2,
                "name": "Tote bag blanc avec un imprimé au choix",
                "images": [
                    "http://localhost:8000/media/listings/2021/06/01/tote-bag-bleu.jpg"
                ],
                "stock": 5,
                "is_available": true,
                "price": 25,
                "attr_name": "couleur bleue",
                "categories": [
                    {
                    "id": 1,
                    "name": "Accessoires"
                    }
                ]
                },
            ]
        """
        variants = []
        representation = {
            "id": instance.pk,
            "variants": variants
        }
        characteristics = instance.characteristics.all()
        for characteristic in characteristics:
            for variant in characteristic.choices.all():
                v = {}
                v['id'] = variant.id
                v['attr_name'] = variant.name
                v['images'] = list(map(lambda x: x.image.url, variant.images.all()))
                v['name'] = instance.product.name
                v['price'] = instance.product.price
                v['stock'] = variant.stock
                v['is_available'] = variant.is_available
                v['categories'] = AtomicCategorySerializer(instance.categories.all(), many=True).data
                variants.append(v)
        representation['variants'] = variants
        return representation

class ListingSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False, )  # Include the product details
    characteristics = CharacteristicSerializer(many=True, required=False, )
    categories = CategorySerializer(many=True, required=False, )

    class Meta:
        model = Listing
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductSerializer(instance.product).data
        representation['characteristics'] = CharacteristicSerializer(instance.characteristics.all(), many=True).data
        representation['categories'] = CategorySerializer(instance.categories.all(), many=True).data
        return representation

    def create(self, validated_data):
        """
            Not proud of this, but it works.
        """
        characteristics_data = validated_data.pop('characteristics')
        categories_data = validated_data.pop('categories')
        product_data = validated_data.pop('product')

        product, created = Product.objects.get_or_create(**product_data)

        listing = Listing.objects.create(**validated_data, product=product)

        for char_data in characteristics_data:
            serializer = CharacteristicSerializer(data=char_data)
            if serializer.is_valid():
                characteristic = serializer.save()
                listing.characteristics.add(characteristic)
            else:
                warnings.warn(f'Serializer errors: {serializer.errors}')

        for category_data in categories_data:
            serialier = CategorySerializer(data=category_data)
            if serialier.is_valid():
                category = serialier.save()
                listing.categories.add(category)
            else:
                warnings.warn(f'Serializer errors: {serialier.errors}') 
        return listing

    def update(self, instance, validated_data):
        # Use serializer to update ManyToMany fields related to Listing
        if 'product' in validated_data:
            serializer = ProductSerializer(data=validated_data['product'])
            if serializer.is_valid():
                product = serializer.update(instance.product, validated_data['product'])
                instance.product = product
            else:
                warnings.warn(f'Serializer errors: {serializer.errors}')
        if 'characteristics' in validated_data:
            characteristics_data = validated_data.pop('characteristics')
            for char_data in characteristics_data:
                serializer = CharacteristicSerializer(data=char_data)
                if serializer.is_valid():
                    characteristic = serializer.save()
                    instance.characteristics.add(characteristic)
                else:
                    warnings.warn(f'Serializer errors: {serializer.errors}')
        if 'categories' in validated_data:
            categories_data = validated_data.pop('categories')
            for category_data in categories_data:
                serializer = CategorySerializer(data=category_data)
                if serializer.is_valid():
                    category = serializer.save()
                    instance.categories.add(category)
                else:
                    warnings.warn(f'Serializer errors: {serializer.errors}')
        return instance