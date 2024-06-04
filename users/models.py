from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('client', 'Client'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)  # Сделано необязательным
    phone = models.CharField(max_length=255, unique=True)
    surname = models.CharField(max_length=255, blank=True, null=True)  # Сделано необязательным
    patronymic = models.CharField(max_length=255, blank=True, null=True)  # Сделано необязательным
    gender_client = models.CharField(max_length=255, default='not specified')
    age = models.IntegerField(default=0)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
