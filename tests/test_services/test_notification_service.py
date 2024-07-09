# tests/test_services/test_notification_service.py

import pytest
from unittest.mock import MagicMock, patch
from app.services.notification_service import send_email, send_alerts_push_notifications, send_sentiment_shift_push_notifications, send_alerts_email_notifications, send_sentiment_shift_email_notifications


mock_db = MagicMock()
mock_get_mail_list = MagicMock(return_value=["tharindusathsara@gmail.com"])

@patch('app.services.notification_service.get_mail_list', mock_get_mail_list)
@patch('app.services.notification_service.send_email')
def test_send_alerts_email_notifications(mock_send_email):
    alerts_within_range = [
        {
            'identified_product_name': 'Sora',
            'total_sentiment_score': 8,
            'alert_range': [-5, 3]
        }
    ]
    recipient_email = "tharindusathsara@gmail.com"

    result = send_alerts_email_notifications(mock_db, alerts_within_range, recipient_email)

    assert result == {"Email Notifications Sent": 1}
    mock_send_email.assert_called_once_with("Product Sentiment Alert", "Product Test Product has a total sentiment score of 8 which is outside the range of -5 to 3", "tharindusathsara@gmail.com")


@patch('app.services.notification_service.get_mail_list', mock_get_mail_list)
@patch('app.services.notification_service.send_email')
def test_send_sentiment_shift_email_notifications(mock_send_email):
    results_within_range = [
        {
            'platform': 'Test Platform',
            'total_sentiment': 6,
            'alert_range': [4, 2]
        }
    ]
    recipient_email = "tharindusathsara@gmail.com"

    result = send_sentiment_shift_email_notifications(mock_db, results_within_range, recipient_email)

    assert result == {"Email Notifications Sent": 1}
    mock_send_email.assert_called_once_with("Platform Sentiment Alert", "Sentiment for Test Platform has shifted to 6 which is outside the range of 4 to 2", "tharindusathsara@gmail.com")


def test_send_alerts_push_notifications():
    alerts_within_range = [
        {
            'identified_product_name': 'ChatGPT',
            'total_sentiment_score': -9,
            'alert_range': [-5, 9]
        }
    ]

    result = send_alerts_push_notifications(mock_db, alerts_within_range)

    assert result == {"Push Notifications Sent": 1}


def test_send_sentiment_shift_push_notifications():
    results_within_range = [
        {
            'platform': 'Facebook',
            'total_sentiment': 6,
            'alert_range': [-4, -2]
        }
    ]

    result = send_sentiment_shift_push_notifications(mock_db, results_within_range)

    assert result == {"Push Notifications Sent": 1}
