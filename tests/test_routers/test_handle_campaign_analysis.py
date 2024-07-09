# tests/test_routers/test_campaign_analysis.py

from fastapi.testclient import TestClient


def test_create_campaign(test_client: TestClient):
    payload = {
        "platform": "SM01",
        "post_description_part": "Sample description"
    }
    response = test_client.post("/social-media/campaign-analysis/create-campaign", json=payload)
    assert response.status_code == 200


def test_campaign_analysis_details(test_client: TestClient):
    response = test_client.get("/social-media/campaign-analysis/campaign_analysis_details?platform=SM01")
    assert response.status_code == 200
