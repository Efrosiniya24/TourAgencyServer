import pytest


@pytest.mark.django_db
def test_create_tour_service():
    client = APIClient()

    data = {
        "name": "Тестовая услуга",
        "description": "Описание тестовой услуги",
        "price": "100.00"
    }

    response = client.post('/services/', data, format='json')

    assert response.status_code == 201

    created_service = TourService.objects.get(name="Тестовая услуга")
    assert created_service.description == "Описание тестовой услуги"
    assert created_service.price == 100.00
