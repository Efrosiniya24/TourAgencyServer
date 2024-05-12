from datetime import datetime
from unittest import TestCase

import pytest
from rest_framework import status

from application.models import Application


class ApplicationViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.viewset = ApplicationViewSet.as_view({'get': 'list'})

        Application.objects.create(status='accepted')
        Application.objects.create(status='rejected')
        Application.objects.create(status='pending')

    def test_get_accepted_applications(self):
        request = self.factory.get('/applications/?category=accepted')
        response = self.viewset(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'accepted')

    def test_get_rejected_applications(self):
        request = self.factory.get('/applications/?category=rejected')
        response = self.viewset(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'rejected')

    def test_get_pending_applications(self):
        request = self.factory.get('/applications/?category=pending')
        response = self.viewset(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')

    def test_get_invalid_category(self):
        request = self.factory.get('/applications/?category=invalid')
        response = self.viewset(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_change_status_to_accepted(self):
        application = Application.objects.create(status='pending')
        data = {'new_status': 'accepted'}

        request = self.factory.post(f'/applications/{application.pk}/change_status/', data)
        response = self.viewset(request, pk=application.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertEqual(application.status, 'accepted')

    def test_change_status_to_rejected(self):
        application = Application.objects.create(status='pending')
        data = {'new_status': 'rejected'}

        request = self.factory.post(f'/applications/{application.pk}/change_status/', data)
        response = self.viewset(request, pk=application.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertEqual(application.status, 'rejected')

    def test_change_status_to_pending(self):
        application = Application.objects.create(status='accepted')
        data = {'new_status': 'pending'}

@pytest.mark.django_db
def test_create_travel_request(user, tourist_service):
    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "service": tourist_service.pk,
        "travel_date": "2024-01-15",
        "number_of_people": 2,
        "additional_information": "Комментарий к заявке",
    }

    response = client.post('/travel-requests/', data, format='json')

    assert response.status_code == 201

    created_request = TravelRequest.objects.get()
    assert created_request.user == user
    assert created_request.service == tourist_service
    assert created_request.travel_date == datetime.date(2024, 1, 15)
    assert created_request.number_of_people == 2
    assert created_request.additional_information == "Комментарий к заявке"


