from rest_framework import viewsets, generics
from apps.users.permissions import IsAdminOrReadOnly
from .serializers import CategorySerializer, ListingSerializer
from .models import Category, Listing

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().order_by('product__name')
    serializer_class = ListingSerializer
    permission_classes = [IsAdminOrReadOnly]

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
