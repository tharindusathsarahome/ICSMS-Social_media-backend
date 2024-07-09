# tests/test_routers/test_products_keywords.py

from fastapi.testclient import TestClient
from datetime import datetime


def test_add_custom_product(test_client: TestClient):
    payload = {
        "custom_product": "Sora"
    }
    response = test_client.post("/social-media/products-keywords/add_custom_product", json=payload)
    assert response.status_code == 200
    

def test_get_custom_products(test_client: TestClient):
    response = test_client.get("/social-media/products-keywords/custom_products")
    assert response.status_code == 200
    

def test_get_identified_products(test_client: TestClient):
    response = test_client.get("/social-media/products-keywords/identified_products")
    assert response.status_code == 200
    

def test_get_identified_products_by_date(test_client: TestClient):
    response = test_client.get(f"/social-media/products-keywords/identified_products_by_date?startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200
    
