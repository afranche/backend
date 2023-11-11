# Serializers for Category Model, Product Model

import warnings
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
    images = ImageSerializer(many=True)
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
        product_data = validated_data.pop('product')
        images_data = product_data.pop('images')
        product = Product.objects.create(**product_data)
        for image_data in images_data:
            Image.objects.create(**image_data)
        return Listing.objects.create(product=product, **validated_data)