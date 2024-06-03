from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from order.models import Order
from order.serialization import OrderDetailSerializer
from .serializers import UserSerializer
from rest_framework.views import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import jwt, datetime
from django.db.models import Q, Avg, Count
from django_filters import rest_framework as filters
from django.utils import timezone


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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
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


class UserCountView(APIView):
    def get(self, request):
        try:
            count = User.objects.count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AverageAgeView(APIView):
    def get(self, request):
        try:
            average_age = User.objects.all().aggregate(Avg('age'))['age__avg']
            if average_age is not None:
                average_age = int(average_age)  # Преобразование среднего возраста в целое число
            else:
                average_age = 0  # Обработка случая, если в базе данных нет пользователей
            return Response({'average_age': average_age}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenderDistributionView(APIView):
    def get(self, request):
        try:
            gender_counts = User.objects.values('gender_client').annotate(count=Count('gender_client'))
            male_count = next((item['count'] for item in gender_counts if item['gender_client'] == 'm'), 0)
            female_count = next((item['count'] for item in gender_counts if item['gender_client'] == 'f'), 0)
            total = male_count + female_count
            male_percentage = (male_count / total) * 100 if total > 0 else 0
            female_percentage = (female_count / total) * 100 if total > 0 else 0
            return Response({
                'male_percentage': male_percentage,
                'female_percentage': female_percentage
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AverageAgeByGenderView(APIView):
    def get(self, request):
        try:
            average_age_male = User.objects.filter(gender_client='m').aggregate(Avg('age'))['age__avg']
            average_age_female = User.objects.filter(gender_client='f').aggregate(Avg('age'))['age__avg']
            if average_age_male is not None:
                average_age_male = int(average_age_male)  # Convert to integer
            else:
                average_age_male = 0  # Handle case if no male users
            if average_age_female is not None:
                average_age_female = int(average_age_female)  # Convert to integer
            else:
                average_age_female = 0  # Handle case if no female users
            return Response({
                'average_age_male': average_age_male,
                'average_age_female': average_age_female
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserCountViewData(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        try:
            if start_date and end_date:
                start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
                end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))
                count = User.objects.filter(date_joined__range=[start_date, end_date]).count()
            else:
                count = User.objects.count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AverageAgeViewData(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        try:
            if start_date and end_date:
                start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
                end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))
                average_age = User.objects.filter(date_joined__range=[start_date, end_date]).aggregate(Avg('age'))['age__avg']
            else:
                average_age = User.objects.all().aggregate(Avg('age'))['age__avg']
            if average_age is not None:
                average_age = int(average_age)  # Преобразование среднего возраста в целое число
            else:
                average_age = 0  # Обработка случая, если в базе данных нет пользователей
            return Response({'average_age': average_age}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenderDistributionViewData(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        try:
            if start_date and end_date:
                start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
                end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))
                gender_counts = User.objects.filter(date_joined__range=[start_date, end_date]).values('gender_client').annotate(count=Count('gender_client'))
            else:
                gender_counts = User.objects.values('gender_client').annotate(count=Count('gender_client'))
            male_count = next((item['count'] for item in gender_counts if item['gender_client'] == 'm'), 0)
            female_count = next((item['count'] for item in gender_counts if item['gender_client'] == 'f'), 0)
            total = male_count + female_count
            male_percentage = (male_count / total) * 100 if total > 0 else 0
            female_percentage = (female_count / total) * 100 if total > 0 else 0
            return Response({
                'male_percentage': male_percentage,
                'female_percentage': female_percentage
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AverageAgeByGenderViewData(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        try:
            if start_date and end_date:
                start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
                end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))
                average_age_male = User.objects.filter(gender_client='m', date_joined__range=[start_date, end_date]).aggregate(Avg('age'))['age__avg']
                average_age_female = User.objects.filter(gender_client='f', date_joined__range=[start_date, end_date]).aggregate(Avg('age'))['age__avg']
            else:
                average_age_male = User.objects.filter(gender_client='m').aggregate(Avg('age'))['age__avg']
                average_age_female = User.objects.filter(gender_client='f').aggregate(Avg('age'))['age__avg']
            if average_age_male is not None:
                average_age_male = int(average_age_male)  # Convert to integer
            else:
                average_age_male = 0  # Handle case if no male users
            if average_age_female is not None:
                average_age_female = int(average_age_female)  # Convert to integer
            else:
                average_age_female = 0  # Handle case if no female users
            return Response({
                'average_age_male': average_age_male,
                'average_age_female': average_age_female
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)