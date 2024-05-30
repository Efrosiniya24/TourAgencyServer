# filters.py
from django_filters import rest_framework as filters
from .models import Order

class OrderFilter(filters.FilterSet):
    user_name = filters.CharFilter(field_name='user__name', lookup_expr='icontains')
    user_surname = filters.CharFilter(field_name='user__surname', lookup_expr='icontains')
    user_patronymic = filters.CharFilter(field_name='user__patronymic', lookup_expr='icontains')
    tour_name = filters.CharFilter(field_name='tour__name', lookup_expr='icontains')
    travel_agency = filters.CharFilter(field_name='tour__travelAgency', lookup_expr='icontains')

    class Meta:
        model = Order
        fields = ['user_name', 'user_surname', 'user_patronymic', 'tour_name', 'travel_agency']
