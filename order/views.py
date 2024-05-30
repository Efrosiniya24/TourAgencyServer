from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.response import Response

from users.models import User
from .filters import OrderFilter

from .models import Order, Tour
from .serialization import OrderSerializer, OrderDetailSerializer

from rest_framework.exceptions import ValidationError


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]  # Позволить всем пользователям доступ

    def perform_create(self, serializer):
        tour_id = self.request.data.get('tour')
        user_id = self.request.data.get('user_id')  # Получить ID пользователя из запроса

        try:
            tour = Tour.objects.get(id=tour_id)
        except Tour.DoesNotExist:
            raise ValidationError('Invalid tour ID')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError('Invalid user ID')

        serializer.save(user=user, tour=tour)


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'


class OrderSearchView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter

    def post(self, request, *args, **kwargs):
        filterset = self.filterset_class(data=request.data, queryset=self.get_queryset())

        if filterset.is_valid():
            queryset = filterset.qs
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)