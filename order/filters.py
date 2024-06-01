from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Order

class OrderSearchFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_by_all_fields')

    class Meta:
        model = Order
        fields = ['search']

    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(
            Q(user__name__icontains=value) |
            Q(user__surname__icontains=value) |
            Q(user__patronymic__icontains=value) |
            Q(tour__name__icontains=value) |
            Q(tour__travelAgency__icontains=value)
        )
