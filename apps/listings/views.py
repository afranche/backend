import base64
from rest_framework import viewsets, generics
from django.core.files.base import ContentFile

from apps.listings.pagination import CategoryPagination, ListingPagination
from apps.users.permissions import IsAdminOrReadOnly
from .serializers import CategorySerializer, ListingSerializer
from .models import Category, Listing


def decode_base64_file(data):
    # check if data is base64 encoded
    image = data.get('image')
    if not image.startswith('data:image'):
        return None

    # Decode the base64 image data
    try:
        image_data = base64.b64decode(image.split(',')[1])
        return ContentFile(image_data, name=f'{data["name"]}-cover.png')
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

    def create(self, request, *args, **kwargs):
        images = request.data.getlist('images')
        images_b64 = [decode_base64_file(image) for image in images]
        request.data.setlist('images', images_b64)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        images = request.data.getlist('images')
        images_b64 = [decode_base64_file(image) for image in images]
        request.data.setlist('images', images_b64)
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
    serializer_class = ListingSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ListingPagination

    def get_queryset(self):
        queryset = Listing.objects.all()

        filters = self.request.query_params

        if 'additional_price' in filters:
            queryset = queryset.filter(additional_price=filters['additional_price'])

        if 'category_name' in filters:
            queryset = queryset.filter(categories__name__icontains=filters['category_name'])

        if 'name' in filters:
            queryset = queryset.filter(product__name__icontains=filters['name'])
        
        if 'description' in filters:
            queryset = queryset.filter(product__description__icontains=filters['description'])

        return queryset
