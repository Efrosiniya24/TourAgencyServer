from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tour

from django_filters import rest_framework as filters
from django.db.models import Q

from .serialzation import TourSerializer


class Tours(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TourSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TourList(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer


class TourDetail(generics.RetrieveAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    lookup_field = 'id'


class TourDelete(APIView):
    def delete(self, request, id, *args, **kwargs):
        try:
            tour = Tour.objects.get(id=id)
            tour.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Tour.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TourUpdate(APIView):
    def put(self, request, id, *args, **kwargs):
        try:
            tour = Tour.objects.get(id=id)
        except Tour.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TourSerializer(tour, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TourSearchFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_by_all_fields')

    class Meta:
        model = Tour
        fields = ['search']

    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(country__icontains=value) |
            Q(city__icontains=value)
        )


class TourSearch(APIView):
    def post(self, request, *args, **kwargs):
        filter_set = TourSearchFilter(request.data, queryset=Tour.objects.all())
        if filter_set.is_valid():
            serializer = TourSerializer(filter_set.qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(filter_set.errors, status=status.HTTP_400_BAD_REQUEST)

class TourCreate(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TourSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)