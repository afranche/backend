# urls for ProductViewset and CategoryViewset

from rest_framework import routers
from django.urls import path, include
from .views import CategoryFilterAPIView, CategoryViewSet, CouponViewSet, ListingFilterAPIView, ListingViewSet

router = routers.DefaultRouter()
router.register('product', ListingViewSet)
router.register('category', CategoryViewSet)
router.register('gertrude', CouponViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('categories/filter', CategoryFilterAPIView.as_view(), name='category-filter-api'),
    path('listings/filter', ListingFilterAPIView.as_view(), name='listing-filter-api'),
]
