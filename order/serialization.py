from rest_framework import serializers

from tours.serialzation import TourDetailSerializer
from users.serializers import UserDetailSerializer
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = '__all__'

class OrderDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    tour = TourDetailSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
