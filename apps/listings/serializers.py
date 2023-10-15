# Serializers for Category Model, Product Model

from rest_framework import serializers
from .models import Category, Product, Characteristic, Listing

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'manufacturer', 'price', 'weight', 'conservation', 'lang', 'images', 'description']

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
        product = validated_data.pop('product')

        product, created = Product.objects.get_or_create(**product)
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
            product.images = product_data.get('images', product.images)
            product.description = product_data.get('description', product.description)
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
