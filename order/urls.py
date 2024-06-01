from django.urls import path
from .views import OrderCreateView, OrderListView, OrderDetailView, OrderSearchView, OrderStatusUpdateView, \
    OrderCountView, ProcessingOrderCountView, AcceptedOrderCountView, RejectedOrderCountView

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('allOrders/', OrderListView.as_view(), name='order-list'),
    path('<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('search/', OrderSearchView.as_view(), name='order-search'),
    path('update-status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('order-count/', OrderCountView.as_view(), name='order-count'),
    path('processing-count/', ProcessingOrderCountView.as_view(), name='processing-order-count'),
    path('accepted-count/', AcceptedOrderCountView.as_view(), name='accepted-order-count'),
    path('rejected-count/', RejectedOrderCountView.as_view(), name='rejected-order-count'),

]
