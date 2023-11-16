from rest_framework import viewsets, generics

from rest_framework.permissions import IsAdminUser

from apps.listings.pagination import DefaultPagination
from apps.users.permissions import IsAdminOrReadOnly
from .serializers import CategorySerializer, ListingSerializer, AtomicListingSerializer
from .models import Category, Listing
from .serializers import CategorySerializer, CouponSerializer, ListingSerializer
from .models import Category, Coupon, Listing

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DefaultPagination

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().order_by('product__name')
    serializer_class = ListingSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DefaultPagination


class CategoryFilterAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DefaultPagination

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
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = Listing.objects.all()

        filters = self.request.query_params

        if 'price' in filters:
            queryset = queryset.filter(product__price=filters['price'])

        if 'category_name' in filters:
            queryset = queryset.filter(categories__name__icontains=filters['category_name'])

        if 'name' in filters:
            queryset = queryset.filter(product__name__icontains=filters['name'])

        if 'manufacturer' in filters:
            queryset = queryset.filter(product__manufacturer__icontains=filters['manufacturer'])
        
        return queryset

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]
    pagination_class = DefaultPagination