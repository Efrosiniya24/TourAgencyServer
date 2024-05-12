from datetime import datetime

from rest_framework import generics


class AnalyticsView(generics.ListAPIView):
    serializer_class = UserActivitySerializer

    def get_queryset(self):
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        queryset = UserActivity.objects.all()

        if start_date_str and end_date_str:
            try:
                start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__range=(start_date, end_date))
            except ValueError:
                pass  # Handle invalid date format

        return queryset
