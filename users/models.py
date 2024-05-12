from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    surname = models.CharField(max_length=255, unique=False)
    patronymic = models.CharField(max_length=255, unique=False)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
