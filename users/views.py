from django.contrib.auth import get_user_model, authenticate
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

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


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            refresh.payload.update({
                'user_id': user.id,
                'username': user.email
            })
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response({'error': 'Нужен и логин, и пароль'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return Response({'error': 'Аккаунт неактивен'}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            user = None

        if user is None:
            return Response({'error': 'Неверные данные'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=email, password=password)
        if user is None:
            return Response({'error': 'Неверные данные'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        refresh.payload.update({
            'user_id': user.id,
            'username': user.email
        })

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'id': user.id,
            'role': user.role
        }, status=status.HTTP_200_OK)

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
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Необходим Refresh token'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except Exception as e:

            return Response({'error': 'Неверный Refresh token'},

                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Выход успешен'}, status=status.HTTP_200_OK)


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