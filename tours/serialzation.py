from rest_framework import serializers
from .models import Tour
from .utils import parse_custom_date


class CustomDateField(serializers.DateField):
    def to_internal_value(self, value):
        return parse_custom_date(value)


class TourSerializer(serializers.ModelSerializer):
    beginningDate = CustomDateField()
    endDate = CustomDateField()

    class Meta:
        model = Tour
        fields = '__all__'


class TourDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ['name', 'description', 'travelAgency']
