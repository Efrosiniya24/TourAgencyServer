from django.db import models

from tours.models import Tour
from users.models import User


class Order(models.Model):
    date = models.DateField()
    status = models.CharField(max_length=255)
    numberOfPeople = models.IntegerField()
    specialRequests = models.TextField(max_length=2000)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

