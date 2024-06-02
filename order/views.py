from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .models import Order, Tour
from .filters import OrderSearchFilter
from .serialization import OrderSerializer, OrderDetailSerializer

from rest_framework.exceptions import ValidationError


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        tour_id = self.request.data.get('tour')
        user_id = self.request.data.get('user_id')

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


class OrderSearchView(APIView):
    def post(self, request, *args, **kwargs):
        filter_set = OrderSearchFilter(request.data, queryset=Order.objects.all())
        print('Search request data:', request.data)  # Добавлено для отладки
        if filter_set.is_valid():
            queryset = filter_set.qs
            print('Filtered queryset:', queryset)  # Добавлено для отладки
            serializer = OrderDetailSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(filter_set.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.AllowAny]  # Настройте доступ по необходимости

    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        new_status = request.data.get('status')

        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save()
            return Response({"status": "success", "message": "Order status updated successfully."},
                            status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"status": "error", "message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)


class OrderCountView(APIView):
    def get(self, request):
        try:
            count = Order.objects.count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProcessingOrderCountView(APIView):
    def get(self, request):
        try:
            count = Order.objects.filter(status='processing').count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AcceptedOrderCountView(APIView):
    def get(self, request):
        try:
            count = Order.objects.filter(status='accepted').count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RejectedOrderCountView(APIView):
    def get(self, request):
        try:
            count = Order.objects.filter(status='rejected').count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserOrdersView(APIView):

    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        orders = Order.objects.filter(user=user)
        serializer = OrderDetailSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderUser(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(user_id=user_id)
        if not orders.exists():
            return Response({'error': 'No orders found for this user'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderDetailSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
