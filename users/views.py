from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.views import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import jwt, datetime
from django.db.models import Q
from django_filters import rest_framework as filters


class SignUp(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SignIn(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload = {
            'id': user.id,
            'exp': timezone.now() + timezone.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()

        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'jwt': token}
        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated")

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated")

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success',
        }
        return response


class AllUsersView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    surname = filters.CharFilter(field_name='surname', lookup_expr='icontains')
    patronymic = filters.CharFilter(field_name='patronymic', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['name', 'surname', 'patronymic']

class UserSearch(generics.ListAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name', '')
        surname = data.get('surname', '')
        patronymic = data.get('patronymic', '')

        queryset = User.objects.none()

        if name or surname or patronymic:
            # Формируем Q-объекты для поиска по каждому параметру
            query = Q()
            if name:
                query |= Q(name__icontains=name)
            if surname:
                query |= Q(surname__icontains=surname)
            if patronymic:
                query |= Q(patronymic__icontains=patronymic)

            queryset = User.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
