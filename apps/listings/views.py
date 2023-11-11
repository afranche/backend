import base64
from uuid import uuid4
import warnings
from rest_framework import viewsets, generics
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from apps.listings.pagination import CategoryPagination, ListingPagination
from apps.users.permissions import IsAdminOrReadOnly
from .serializers import CategorySerializer, ListingSerializer, AtomicListingSerializer
from .models import Category, Listing


def decode_base64_file(data):

    # check if data is base64 encoded
    image = data.get('image')
    name = data.get('name', uuid4().__str__() + '-cover.png')

    if isinstance(image, InMemoryUploadedFile) or isinstance(image, TemporaryUploadedFile) \
        or isinstance(image, ContentFile):
        return image

    if not image.startswith('data:image'):
        return ContentFile(image, name=name)

    # Decode the base64 image data
    try:
        image_data = base64.b64decode(image.split(',')[1])
        return ContentFile(image_data, name=name)
    except Exception as e:
        return None

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CategoryPagination

    def create(self, request, *args, **kwargs):
        request.data['image'] = decode_base64_file(request.data)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data['image'] = decode_base64_file(request.data)
        return super().update(request, *args, **kwargs)


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().order_by('product__name')
    serializer_class = ListingSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ListingPagination

    def perform_create(self, serializer):
        serializer.save()  # Call serializer.save() to create and save the object

    def create(self, request, *args, **kwargs):
        product_data = request.data.get('product', {})
        images = product_data.get('images', [])
        
        if images:
            product_data['images'] = [
                {"image": decode_base64_file(image)} for image in images
            ]
        
        request.data['product'] = product_data
        warnings.warn(f'request.data: {request.data}')
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            warnings.warn(f'Exception: {e}')
            warnings.warn(f'serializer.errors: {serializer.errors}')
            warnings.warn(f'serializer.initial_data: {serializer.initial_data}')

        warnings.warn(f'serializer.Data: {serializer.data}')
        self.perform_create(serializer)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        product_data = request.data.get('product', {})
        images = product_data.get('images', [])

        if images:
            product_data['images'] = [
                {"image": decode_base64_file(image)} for image in images
            ]

        request.data['product'] = product_data
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Listing.objects.all().order_by('product__name')
        category = self.request.query_params.get('category', None)
        name = self.request.query_params.get('name', None)
        if category is not None:
            queryset = queryset.filter(category__name=category)
        if name is not None:
            queryset = queryset.filter(product__name__icontains=name)
        return queryset


class CategoryFilterAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CategoryPagination

    def get_queryset(self):
        queryset = Category.objects.all()
        filters = self.request.query_params

        if 'name' in filters:
            queryset = queryset.filter(name__icontains=filters['name'])

        if 'language' in filters:
            queryset = queryset.filter(language=filters['language'])
        
        if 'parent' in filters:
            queryset = queryset.filter(parent=None if filters['parent'] == "null" else  filters['parent'])
        
        if 'description' in filters:
            queryset = queryset.filter(description__icontains=filters['description'])

        return queryset

class ListingFilterAPIView(generics.ListAPIView):
    serializer_class = AtomicListingSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ListingPagination

    def get_queryset(self):
        queryset = Listing.objects.all()

        filters = self.request.query_params

        if 'price' in filters:
            queryset = queryset.filter(product__price=filters['price'])

        if 'category_name' in filters:
            queryset = queryset.filter(categories__name__icontains=filters['category_name'])

        if 'name' in filters:
            queryset = queryset.filter(product__name__icontains=filters['name'])
        
        return queryset
