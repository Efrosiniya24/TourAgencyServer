from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, unique=True)
    surname = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255)
    gender_client = models.CharField(max_length=255, default='not specified')
    age = models.IntegerField(default=0)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

