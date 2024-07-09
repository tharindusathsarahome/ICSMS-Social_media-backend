# tests/test_routers/test_handle_dashboard.py

from fastapi.testclient import TestClient


def test_facebook_analysis_data(test_client: TestClient):
    response = test_client.get("/social-media/dashboard/facebook_analysis_data?startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200


def test_instagram_analysis_data(test_client: TestClient):
    response = test_client.get("/social-media/dashboard/instagram_analysis_data?startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200


def test_product_trend_data(test_client: TestClient):
    response = test_client.get("/social-media/dashboard/product_trend_data?startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200


def test_keyword_trend_data(test_client: TestClient):
    response = test_client.get("/social-media/dashboard/keyword_trend_data?startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200


def test_get_sentiment_percentage(test_client: TestClient):
    response = test_client.get("/social-media/dashboard/get_setiment_percentage?startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200


def test_sentimentscore_facebook(test_client: TestClient):
    response = test_client.get("/social-media/dashboard/sentimentscore_facebook?startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200


def test_sentimentscore_instagram(test_client: TestClient):
    response = test_client.get("/social-media/dashboard/sentimentscore_instagram?startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200

