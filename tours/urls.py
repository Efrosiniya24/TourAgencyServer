from django.urls import path, include
from .views import Tours, TourList

urlpatterns = [
    path('addTour', Tours.as_view(), name='addTour'),
    path('allTours', TourList.as_view(), name='allTours'),

]
