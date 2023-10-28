# urls for ProductViewset and CategoryViewset

from rest_framework import routers
from django.urls import path, include
from .views import CategoryFilterAPIView, CategoryViewSet, ListingFilterAPIView, ListingViewSet

router = routers.DefaultRouter()
router.register('product', ListingViewSet)
router.register('category', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/categories/filter/', CategoryFilterAPIView.as_view(), name='category-filter-api'),
    path('api/listings/filter/', ListingFilterAPIView.as_view(), name='listing-filter-api'),
]