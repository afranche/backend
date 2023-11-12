# Serializers for Category Model, Product Model

import warnings
from rest_framework import serializers
from .models import Category, Product, Characteristic, Listing

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


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListSerializer(child=serializers.CharField())
    class Meta:
        model = Product
        fields = ['id', 'name', 'manufacturer', 'price', 'weight', 'conservation', 'lang', 'images', 'description']

class AtomicListingSerializer(serializers.ModelSerializer):

    categories = AtomicCategorySerializer(many=True)
    images = serializers.ListSerializer(child=serializers.CharField(), source='product.images')
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductSerializer(instance.product).data
        representation['characteristics'] = CharacteristicSerializer(instance.characteristics, many=True).data
        representation['categories'] = CategorySerializer(instance.categories, many=True).data
        warnings.warn(f'representation: {representation}')
        return representation

    def create(self, validated_data):
        characteristics_data = validated_data.pop('characteristics')
        categories_data = validated_data.pop('categories')
        product_data = validated_data.pop('product')
        images_data = product_data.pop('images', [])

        product, created = Product.objects.get_or_create(**product_data)

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