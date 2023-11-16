from rest_framework import viewsets
from apps.listings.pagination import DefaultPagination

from apps.users.permissions import IsOwnerOrAdmin
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsOwnerOrAdmin]