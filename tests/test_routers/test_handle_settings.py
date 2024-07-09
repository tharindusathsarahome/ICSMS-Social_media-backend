# tests/test_routers/test_settings.py

from fastapi.testclient import TestClient

def test_all_campaigns(test_client: TestClient):
    response = test_client.get("/social-media/settings/campaigns")
    assert response.status_code == 200
    

def test_delete_campaign(test_client: TestClient):
    campaign_id = "667e20c321cd5a056b0e1272"
    response = test_client.delete(f"/social-media/settings/campaign/{campaign_id}")
    assert response.status_code == 200
    

def test_add_product_alert(test_client: TestClient):
    payload = {
        "product": "ChatGPT",
        "alert_type": "email",
        "min_val": -2,
        "max_val": 5
    }
    response = test_client.post("/social-media/settings/add_product_alert", json=payload)
    assert response.status_code == 200
    

def test_get_product_alert(test_client: TestClient):
    alert_id = "66864d628aaebf78b5640c2b"
    response = test_client.get(f"/social-media/settings/product_alert/{alert_id}")
    assert response.status_code == 200
    

def test_get_all_product_alerts(test_client: TestClient):
    response = test_client.get("/social-media/settings/product_alerts")
    assert response.status_code == 200
    

def test_update_product_alert(test_client: TestClient):
    alert_id = "66864d628aaebf78b5640c2b"
    payload = {
        "alert_type": "app",
        "min_val": -2,
        "max_val": 5
    }
    response = test_client.put(f"/social-media/settings/product_alert/{alert_id}", json=payload)
    assert response.status_code == 200
    

def test_delete_product_alert(test_client: TestClient):
    alert_id = "66864d628aaebf78b5640c2b"
    response = test_client.delete(f"/social-media/settings/product_alert/{alert_id}")
    assert response.status_code == 200
    

def test_get_sentiment_shift_threshold(test_client: TestClient):
    response = test_client.get("/social-media/settings/sentiment_shifts")
    assert response.status_code == 200
    

def test_add_sentiment_shift_threshold(test_client: TestClient):
    payload = {
        "sm_id": "SM01",
        "alert_type": "email",
        "min_val": -2,
        "max_val": 8
    }
    response = test_client.post("/social-media/settings/add_sentiment_shift_threshold", json=payload)
    assert response.status_code == 200
    

def test_get_sentiment_shift_threshold_by_id(test_client: TestClient):
    threshold_id = "6682eed10ea600e48536e784"
    response = test_client.get(f"/social-media/settings/sentiment_shift_threshold/{threshold_id}")
    assert response.status_code == 200
    

def test_update_sentiment_shift_threshold(test_client: TestClient):
    threshold_id = "6682eed10ea600e48536e784"
    payload = {
        "sm_id": "SM01",
        "alert_type": "email",
        "min_val": -5,
        "max_val": 3
    }
    response = test_client.put(f"/social-media/settings/sentiment_shift_threshold/{threshold_id}", json=payload)
    assert response.status_code == 200
    

def test_delete_sentiment_shift_threshold(test_client: TestClient):
    threshold_id = "6682eed10ea600e48536e784"
    response = test_client.delete(f"/social-media/settings/sentiment_shift_threshold/{threshold_id}")
    assert response.status_code == 200
    

def test_read_notification_settings(test_client: TestClient):
    response = test_client.get("/social-media/settings/notifications")
    assert response.status_code == 200
    

def test_update_notification_settings(test_client: TestClient):
    payload = {
        "dashboard_notifications": True,
        "email_notifications": False,
        "notification_emails": ["test@gmail.com"]
    }
    response = test_client.put("/social-media/settings/notifications", json=payload)
    assert response.status_code == 200
