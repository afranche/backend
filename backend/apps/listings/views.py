from rest_framework import viewsets

from rest_framework.permissions import IsAdminUser

from apps.listings.pagination import CategoryPagination, DefaultPagination, ListingPagination
from apps.users.permissions import IsAdminOrReadOnly
from .serializers import CategorySerializer, CouponSerializer, ListingSerializer, ManufacturerSerializer
from .models import Category, Coupon, Listing, Manufacturer
from rest_framework import status
from rest_framework.response import Response

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CategoryPagination

    def get_queryset(self):
        queryset = Category.objects.all()
        length = queryset.count()
        filters = self.request.query_params

        if 'name' in filters and isinstance(filters['name'], str):
            queryset = queryset.filter(name__icontains=filters['name'])

        if 'language' in filters and isinstance(filters['language'], str):
            queryset = queryset.filter(language=filters['language'])
        
        if 'parent' in filters and isinstance(filters['parent'], str):
            queryset = queryset.filter(parent=None if filters['parent'] == "null" else  filters['parent'])
        
        if 'description' in filters and isinstance(filters['description'], str):
            queryset = queryset.filter(description__icontains=filters['description'])

        if length != queryset.count() and len(filters) != 0:
            return []
        return queryset

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().order_by('name')
    serializer_class = ListingSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ListingPagination

    def get_queryset(self):
        queryset = Listing.objects.all()
        length = queryset.count()
        filters = self.request.query_params

        if 'price' in filters and filters['price'].isdigit():
            queryset = queryset.filter(price=filters['price'])

        if 'category_name' in filters and isinstance(filters['category_name'], str):
            queryset = queryset.filter(categories__name__icontains=filters['category_name'])

        if 'name' in filters and isinstance(filters['name'], str):
            queryset = queryset.filter(name__icontains=filters['name'])

        if 'manufacturer' in filters and isinstance(filters['manufacturer'], str):
            queryset = queryset.filter(manufacturer__name__icontains=filters['manufacturer'])
        if length != queryset.count() and len(filters) != 0:
            return []
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [IsAdminOrReadOnly]

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]
    pagination_class = DefaultPagination