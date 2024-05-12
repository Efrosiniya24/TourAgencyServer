import pytest


@pytest.mark.django_db
def test_order_history(user_with_orders):
    client = APIClient()
    client.force_authenticate(user=user_with_orders)

    response = client.get('/order-history/')

    assert response.status_code == 200

    data = response.json()
    assert len(data) == user_with_orders.order_set.count()
