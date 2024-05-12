import datetime
from unittest import TestCase
from unittest.mock import patch

from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer


class SignUpTestCase(APITestCase):
    def test_user_registration(self):
        url = reverse('signUp')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'name': 'Test',
            'phone': '1234567890',
            'surname': 'TestSurname',
            'patronymic': 'TestPatronymic'
        }
        response = self.client.post(url, data, format='json')
        self.assertTrue('id' in response.data)
        self.assertTrue('email' in response.data)
        self.assertEqual(response.data['email'], data['email'])


class UserViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            email='test@example.com',
            password='testpassword',
            name='Test',
            phone='1234567890',
            surname='TestSurname',
            patronymic='TestPatronymic'
        )
        self.token = 'test_token'

    @patch('backend.users.views.jwt.decode')
    def test_get_user_authenticated(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {'id': self.user.id}
        url = reverse('user-view')
        response = self.client.get(url, HTTP_COOKIE=f'jwt={self.token}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(response.data['email'], self.user.email)

    def test_get_user_unauthenticated(self):
        url = reverse('user-view')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AllUsersView(TestCase):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
