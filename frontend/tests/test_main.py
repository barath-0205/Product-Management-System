import pytest
from unittest.mock import patch, Mock
import requests

# Importing your helper functions (adjust path if needed)
from frontend.main import get_data, create_data, update_data, delete_data, login

API_URL = "http://localhost:8000"

# ---- LOGIN TEST ----
@patch("frontend.main.requests.post")
def test_login_success(mock_post):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "sample_token", "token_type": "bearer"}
    mock_post.return_value = mock_response

    login("test@example.com", "securepassword")
    print("✅ Login function executed successfully")

@patch("frontend.main.requests.get")
def test_get_products(mock_get):
    sample_response = [{"id": 1, "name": "Test Product", "price": 10.0}]
    mock_get.return_value = Mock(status_code=200, json=lambda: sample_response)

    result = get_data("products")
    assert isinstance(result, list)
    assert result[0]["name"] == "Test Product"
    print("✅ get_data(products) returned:", result)

@patch("frontend.main.requests.post")
def test_create_product(mock_post):
    mock_post.return_value = Mock(status_code=201, json=lambda: {"message": "Created"})
    payload = {
        "name": "Test Product",
        "category": "Electronics",
        "price": 100.0,
        "stock": 10,
        "sku": "TP123",
        "supplier_id": 1,
        "status": "active"
    }
    response = create_data("createProduct", payload)
    assert response.status_code == 201
    print("✅ create_data(product) called with payload:", payload)

@patch("frontend.main.requests.put")
def test_update_product(mock_put):
    mock_put.return_value = Mock(status_code=200, json=lambda: {"update": "success"})
    update_payload = {"name": "Updated Product"}
    response = update_data("updateProduct/1", update_payload)
    assert response.status_code == 200
    print("✅ update_data(product) updated with:", update_payload)

@patch("frontend.main.requests.delete")
def test_delete_product(mock_delete):
    mock_delete.return_value = Mock(status_code=200, json=lambda: {"update": "deleted"})
    response = delete_data("deleteProduct/1")
    assert response.status_code == 200
    print("✅ delete_data(product) deleted product with ID 1")
