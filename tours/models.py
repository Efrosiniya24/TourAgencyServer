from django.db import models


class Tour(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=255)
    numberOfDays = models.IntegerField()
    price = models.IntegerField()
    beginningDate = models.DateField()
    endDate = models.DateField()
    city = models.CharField(max_length=255)
    description = models.TextField(max_length=2000)
    program = models.TextField(max_length=500000)
    travelAgency = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.country} - {self.city} ({self.beginningDate} to {self.endDate})"