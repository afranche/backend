from django.shortcuts import render
from rest_framework import viewsets
from apps.listings.pagination import DefaultPagination

from apps.users.permissions import IsAdminOrReadOnly

from .serializers import OrderSerializer
from .models import Order


class OrderViewset(viewsets.ModelViewSet):
    queryset = Order.objects.all()  # type: ignore
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DefaultPagination


