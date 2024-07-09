# tests/test_routers/test_platform_insights.py

from fastapi.testclient import TestClient


def test_keyword_trend_count(test_client: TestClient):
    response = test_client.get("/social-media/platform-insights/keyword_trend_count?platform=SM01&startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200
    

def test_total_reactions(test_client: TestClient):
    response = test_client.get("/social-media/platform-insights/total_reactions?platform=SM01&startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200
    

def test_total_comments(test_client: TestClient):
    response = test_client.get("/social-media/platform-insights/total_comments?platform=SM01&startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200
    

def test_highlighted_comments(test_client: TestClient):
    response = test_client.get("/social-media/platform-insights/highlighted_comments?platform=SM01&startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200
    

def test_average_sentiment_score(test_client: TestClient):
    response = test_client.get("/social-media/platform-insights/average_sentiment_score?platform=SM01&startDate=2024-01-01&endDate=2024-06-30")
    assert response.status_code == 200
    
