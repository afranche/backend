# urls for ProductViewset and CategoryViewset

from rest_framework import routers
from django.urls import path, include
from .views import CategoryViewSet, CouponViewSet, ListingViewSet, ManufacturerViewSet

router = routers.DefaultRouter()
router.register('product', ListingViewSet)
router.register('category', CategoryViewSet)
router.register('manufacturer', ManufacturerViewSet)
router.register('gertrude', CouponViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
