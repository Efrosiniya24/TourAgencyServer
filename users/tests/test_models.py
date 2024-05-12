from django.test import TestCase

from users.models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name='TestName',
            email='test@example.com',
            phone='1234567890',
            password='testpassword',
            surname='TestSurname',
            patronymic='TestPatronymic'
        )

    def test_user_creation(self):
        """Тест на создание пользователя"""
        self.assertEqual(self.user.name, 'TestName')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.phone, '1234567890')
        self.assertEqual(self.user.password, 'testpassword')
        self.assertEqual(self.user.surname, 'TestSurname')
        self.assertEqual(self.user.patronymic, 'TestPatronymic')
