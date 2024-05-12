from django.db import models


class Tour():
    country = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    surname = models.CharField(max_length=255, unique=False)
    patronymic = models.CharField(max_length=255, unique=False)
