# Serializers for Category Model, Product Model

import warnings
from rest_framework import serializers
from .models import Category, ImageModel, Manufacturer, Product, Listing, base64_image_to_file


class Base64ImageField(serializers.FileField):
    def to_internal_value (self, data) :
        if isinstance(data, str) and (data.startswith('http://') or data.startswith('https://')):
            return data
        data = base64_image_to_file(data)
        return super().to_internal_value(data)

class CategorySerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    class Meta:
        model = Category
        fields = '__all__'

class ImageModelSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    class Meta:
        model = ImageModel
        fields = ['id', 'image',]


class ManufacturerSerializer(serializers.ModelSerializer):
    pictures = ImageModelSerializer(many=True, required=False)
    class Meta:
        model = Manufacturer
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    images = ImageModelSerializer(many=True, required=False)
    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        if 'images' in validated_data:
            images = validated_data.pop('images')
            instance = super().create(validated_data)
            for image in images:
                image_serializer = ImageModelSerializer(data=image)
                if image_serializer.is_valid():
                    image_serializer.save()
                    instance.images.add(image_serializer.instance)
                else:
                    warnings.warn(f'errors: {image_serializer.errors}')
            return instance
        return super().create(validated_data)

    def validate(self, attrs):
        characteristics = attrs.get('characteristics')
        if characteristics:
            if not isinstance(characteristics, dict):
                raise serializers.ValidationError("characteristics must be a dict")
            if "label" not in characteristics or "value" not in characteristics:
                raise serializers.ValidationError("characteristics must be a list of dictionaries with keys 'label' and 'value'")
        return super().validate(attrs)
    
    def update(self, instance, validated_data):
        if instance.is_sold:
            return instance
        return super().update(instance, validated_data)
    

class ListingSerializer(serializers.ModelSerializer):
    options = serializers.ListSerializer(child=serializers.JSONField(), required=False)
    class Meta:
        model = Listing
        fields = [
            'id',
            'name',
            'price',
            'description',
            'manufacturer',
            'categories',
            'options'
        ]

    def to_representation(self, instance):
        """
            We want to flatten the products field to be a list of unique products
        """
        representation = super().to_representation(instance)
        filtered_products = Product.objects.filter(
            is_customised=False,
            is_active=True,
            listing__id=instance.id
        )
        unique_products_dict = (
            filtered_products
            .order_by('characteristics__label', 'characteristics__value')
            .distinct('characteristics__label', 'characteristics__value')
        )
        """
            We don't wan'to display all of the customized products, so we flatten them
        """
        customized_products = (
            Product.objects
            .filter(is_customised=True, is_active=True, listing__id=instance.id)
            .order_by('characteristics__label')
            .distinct('characteristics__label')
        )
        representation['products'] = ProductSerializer(instance=unique_products_dict.union(customized_products), many=True).data
        representation['categories'] = list(instance.categories.values('id', 'name', 'image'))
        return representation

    def create(self, validated_data):
        """
            Will receive data like this:
            [
                {
                    "id": 1,
                    "name": "Product Name",
                    "price": 12.0,
                    "description": "Product Description",
                    "manufacturer": 1,
                    "categories": [{
                        "id": 1,
                        "name": "Category Name"
                    }],
                    "options": [
                        {
                            "label": "Color",
                            "id": 1,
                            "value": "Red",
                            "images": [
                                        {
                                    "id": 1,
                                    "image": "http://localhost:8000/media/..."
                                }
                            ],
                            "additional_price": 0.0,
                            "stock": 0,
                            "is_available": false
                        },
                        {
                            "id": 2,
                            "label": "Color",
                            "value": "Blue",
                            "images": [
                                {
                                    "id": 2,
                                    "image": "http://localhost:8000/media/..."
                                }
                            ],
                            "additional_price": 0.0,
                            "stock": 0,
                            "is_available": false
                        }
                    ]
                }
            ]
        """
        options = validated_data.pop('options', [])
        instance = super().create(validated_data)
        products = self.generate_products(options)
        instance.products.add(*map(lambda p: p.instance, products))
        return instance
    
    def generate_products(self, options):
        products = []
        for option in options:
            if 'characteristics' not in option:
                label = option.pop("label", "input")
                stock = option.pop('stock', 1)
                value = option.pop('value', "")
                option['characteristics'] = {'label': label, 'value': value}
            if stock == 0:
                stock = 1
            for _ in range(stock):
                product = ProductSerializer(data=option)
                if product.is_valid():
                    product.save()
                    products.append(product)
                else:
                    warnings.warn(f'errors: {product.errors}')
        return products
    
    def update(self, instance, validated_data):
        """
            For PUT not PATCH. 
            Current configuration doesn't allow for PATCHing the products field
        """
        if 'options' in validated_data:
            options = validated_data.pop('options', [])
            products = self.generate_products(options)
            for product in instance.products.all():
                product.delete()
            instance.products.add(*map(lambda p: p.instance, products))
        return super().update(instance, validated_data)
