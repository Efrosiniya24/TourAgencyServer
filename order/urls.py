from django.urls import path
from .views import OrderCreateView, OrderListView, OrderDetailView, OrderSearchView, OrderStatusUpdateView, \
    OrderCountView, ProcessingOrderCountView, AcceptedOrderCountView, RejectedOrderCountView, UserOrdersView, OrderUser, \
    OrderCountViewData, ProcessingOrderCountViewData, AcceptedOrderCountViewData, RejectedOrderCountViewData, \
    GenerateReportView

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
    path('userOrders', UserOrdersView.as_view(), name='user-orders'),
    path('userOrders', OrderUser.as_view(), name='user_orders'),
    path('order-count-data/', OrderCountViewData.as_view(), name='order-count'),
    path('processing-count-data/', ProcessingOrderCountViewData.as_view(), name='processing-order-count'),
    path('accepted-count-data/', AcceptedOrderCountViewData.as_view(), name='accepted-order-count'),
    path('rejected-count-data/', RejectedOrderCountViewData.as_view(), name='rejected-order-count'),
    path('generate_order_report/', GenerateReportView.as_view(), name='generate_order_report'),
]
