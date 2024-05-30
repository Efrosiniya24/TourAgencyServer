from django.urls import path
from .views import OrderCreateView, OrderListView, OrderDetailView, OrderSearchView

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('allOrders/', OrderListView.as_view(), name='order-list'),
    path('<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('search/', OrderSearchView.as_view(), name='order-search'),
]
