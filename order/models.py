from django.db import models
from tours.models import Tour
from users.models import User

class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    date = models.DateField()
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    numberOfPeople = models.IntegerField()
    specialRequests = models.TextField(max_length=2000)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f"{self.tour} - {self.user} ({self.status})"
