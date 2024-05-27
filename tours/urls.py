from django.urls import path, include
from .views import Tours, TourList, TourDetail, TourDelete, TourUpdate, TourSearch, TourCreate

urlpatterns = [
    path('addTour', Tours.as_view(), name='addTour'),
    path('allTours', TourList.as_view(), name='allTours'),
    path('viewingTour/<int:id>/', TourDetail.as_view(), name='tourDetail'),
    path('deleteTour/<int:id>/', TourDelete.as_view(), name='tourDelete'),
    path('updateTour/<int:id>/', TourUpdate.as_view(), name='tourUpdate'),
    path('search/', TourSearch.as_view(), name='tourSearch'),
    path('create/', TourCreate.as_view(), name='tour-create'),

]
