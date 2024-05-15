from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tour
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
