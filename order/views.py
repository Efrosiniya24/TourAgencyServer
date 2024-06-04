from io import BytesIO

from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
import matplotlib.pyplot as plt
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import Order
from django.db.models import Count

from users.models import User

from .models import Order, Tour
from .filters import OrderSearchFilter
from .serialization import OrderSerializer, OrderDetailSerializer

from rest_framework.exceptions import ValidationError


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        tour_id = self.request.data.get('tour')
        user_id = self.request.data.get('user_id')

        try:
            tour = Tour.objects.get(id=tour_id)
        except Tour.DoesNotExist:
            raise ValidationError('Invalid tour ID')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError('Invalid user ID')

        serializer.save(user=user, tour=tour)


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'


class OrderSearchView(APIView):
    def post(self, request, *args, **kwargs):
        filter_set = OrderSearchFilter(request.data, queryset=Order.objects.all())
        print('Search request data:', request.data)  # Добавлено для отладки
        if filter_set.is_valid():
            queryset = filter_set.qs
            print('Filtered queryset:', queryset)  # Добавлено для отладки
            serializer = OrderDetailSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(filter_set.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.AllowAny]  # Настройте доступ по необходимости

    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        new_status = request.data.get('status')

        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save()
            return Response({"status": "success", "message": "Order status updated successfully."},
                            status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"status": "error", "message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)


class OrderCountView(APIView):
    def get(self, request):
        try:
            count = Order.objects.count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProcessingOrderCountView(APIView):
    def get(self, request):
        try:
            count = Order.objects.filter(status='processing').count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AcceptedOrderCountView(APIView):
    def get(self, request):
        try:
            count = Order.objects.filter(status='accepted').count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RejectedOrderCountView(APIView):
    def get(self, request):
        try:
            count = Order.objects.filter(status='rejected').count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserOrdersView(APIView):

    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        orders = Order.objects.filter(user=user)
        serializer = OrderDetailSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderUser(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(user_id=user_id)
        if not orders.exists():
            return Response({'error': 'No orders found for this user'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderDetailSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCountViewData(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        try:
            if start_date and end_date:
                count = Order.objects.filter(createdAt__range=[start_date, end_date]).count()
            else:
                count = Order.objects.count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProcessingOrderCountViewData(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        try:
            if start_date and end_date:
                count = Order.objects.filter(status='processing', createdAt__range=[start_date, end_date]).count()
            else:
                count = Order.objects.filter(status='processing').count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AcceptedOrderCountViewData(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        try:
            if start_date and end_date:
                count = Order.objects.filter(status='accepted', createdAt__range=[start_date, end_date]).count()
            else:
                count = Order.objects.filter(status='accepted').count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RejectedOrderCountViewData(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        try:
            if start_date and end_date:
                count = Order.objects.filter(status='rejected', createdAt__range=[start_date, end_date]).count()
            else:
                count = Order.objects.filter(status='rejected').count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Используем 'Agg' бэкэнд для Matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from .models import Order

class GenerateReportView(APIView):
    def get(self, request):
        try:
            # Путь к файлу шрифта DejaVuSans
            font_path = "fonts/DejaVuSans.ttf"

            # Регистрация шрифта
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

            # Получаем количество заказов
            total_orders = Order.objects.count()
            processing_orders = Order.objects.filter(status='processing').count()
            accepted_orders = Order.objects.filter(status='accepted').count()
            rejected_orders = Order.objects.filter(status='rejected').count()

            # Создаем PDF документ
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="order_report.pdf"'

            p = canvas.Canvas(response, pagesize=letter)
            width, height = letter

            # Добавляем текущую дату в шапку
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            p.setFont("DejaVuSans", 12)
            p.drawString(30, height - 30, f"Дата отчета: {current_date}")

            # Центрируем заголовок отчета
            p.setFont("DejaVuSans", 16)
            p.drawCentredString(width / 2.0, height - 50, "Отчет по заявкам")

            p.setFont("DejaVuSans", 12)
            p.drawString(30, height - 100, f"Всего заявок: {total_orders}")
            p.drawString(30, height - 120, f"Заявки в обработке: {processing_orders}")
            p.drawString(30, height - 140, f"Принятые заявки: {accepted_orders}")
            p.drawString(30, height - 160, f"Отклоненные заявки: {rejected_orders}")

            # Создаем столбчатую диаграмму
            statuses = ['В обработке', 'Принятые', 'Отклоненные']
            counts = [processing_orders, accepted_orders, rejected_orders]

            plt.figure(figsize=(6, 4))
            plt.bar(statuses, counts, color=['#E4E4E4', '#F4E06E', '#DF9E61'])
            plt.title('Количество заявок по статусам')
            plt.xlabel('Статус заявки')
            plt.ylabel('Количество')

            # Сохраняем диаграмму в буфер
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            # Добавляем диаграмму в PDF
            p.drawImage(ImageReader(buf), 30, height - 450, width=500, height=300)


            p.showPage()
            p.save()

            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
