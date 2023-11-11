# Serializers for Category Model, Product Model

from rest_framework import serializers
from .models import Category, Image, Product, Characteristic, Listing

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AtomicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name',]

class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'manufacturer', 'price', 'weight', 'conservation', 'lang', 'images', 'description']

class AtomicListingSerializer(serializers.ModelSerializer):

    categories = AtomicCategorySerializer(many=True)
    images = ImageSerializer(many=True, read_only=True)
    name = serializers.CharField(source='product.name')
    stock = serializers.IntegerField(source='product.stock')
    is_available = serializers.BooleanField(source='product.is_available')
    price = serializers.FloatField(source='product.price')

    class Meta:
        model = Listing
        fields = ['id',
                  'name',
                  'images',
                  'stock',
                  'is_available',
                  'price',
                  'categories']

class ListingSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Include the product details
    characteristics = CharacteristicSerializer(many=True)
    categories = CategorySerializer(many=True)

    class Meta:
        model = Listing
        fields = '__all__'

    def create(self, validated_data):
        characteristics_data = validated_data.pop('characteristics')
        categories_data = validated_data.pop('categories')
        product_data = validated_data.pop('product')
        images_data = product_data.pop('images', [])

        product, created = Product.objects.get_or_create(**product_data)

        # Creating product images
        for image_data in images_data:
            product.images.add(Image.objects.create(**image_data))
        listing = Listing.objects.create(**validated_data, product=product)

        for char_data in characteristics_data:
            char, created = Characteristic.objects.get_or_create(**char_data)
            listing.characteristics.add(char)

        for category_data in categories_data:
            if isinstance(category_data, int):
                category = Category.objects.get(id=category_data)
            else:
                category, created = Category.objects.get_or_create(**category_data)
            listing.categories.add(category)
        
        return listing

    def update(self, instance, validated_data):
        instance.additional_price = validated_data.get('additional_price', instance.additional_price)
        product_data = validated_data.get('product')
        images_data = product_data.pop('images', [])
    
        if product_data:
            product = instance.product
            product.name = product_data.get('name', product.name)
            product.manufacturer = product_data.get('manufacturer', product.manufacturer)
            product.price = product_data.get('price', product.price)
            product.weight = product_data.get('weight', product.weight)
            product.conservation = product_data.get('conservation', product.conservation)
            product.lang = product_data.get('lang', product.lang)
            product.description = product_data.get('description', product.description)
            product.stock = product_data.get('stock', product.stock)
            product.is_available = product_data.get('is_available', product.is_available)
            product.save()

            # update product images without re uploading exisiting ones
            for image_data in images_data:
                if 'id' in image_data:
                    image = Image.objects.get(id=image_data['id'])
                    image.image = image_data.get('image', image.image)
                    image.save()
                else:
                    product.images.add(Image.objects.create(**image_data))

        characteristics_data = validated_data.get('characteristics')
        categories_data = validated_data.get('categories')

        if characteristics_data:
            # Clear existing characteristics and re-add updated ones
            instance.characteristics.clear()
            for char_data in characteristics_data:
                char, created = Characteristic.objects.get_or_create(**char_data)
                instance.characteristics.add(char)

        if categories_data:
            # Clear existing categories and re-add updated ones
            instance.categories.clear()
            for category_data in categories_data:
                if isinstance(category_data, int):
                    category = Category.objects.get(id=category_data)
                else:
                    category, created = Category.objects.get_or_create(**category_data)
                instance.categories.add(category)

        instance.save()
        return instance
