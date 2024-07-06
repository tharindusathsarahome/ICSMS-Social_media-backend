import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from pymongo import MongoClient
from typing import List, Dict
from app.database.notification_data import add_notification, get_mail_list
from app.core.config import GMAIL_USER, GMAIL_APP_PASSWORD



def send_email(subject: str, body: str, to: str) -> None:
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USER, to, text)
        server.quit()
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")


def send_alerts_push_notifications(db: MongoClient, alerts_within_range: List[Dict]) -> Dict[str, int]:
    for alert in alerts_within_range:
        add_notification(db, "Product Sentiment Alert", f"Product {alert['identified_product_name']} has a total sentiment score of {alert['total_sentiment_score']} which is outside the range of {alert['alert_range'][0]} to {alert['alert_range'][1]}")
    return {"Push Notifications Sent": len(alerts_within_range)}


def send_sentiment_shift_push_notifications(db: MongoClient, results_within_range: List[Dict]) -> Dict[str, int]:
    for alert in results_within_range:
        add_notification(db, "Platform Sentiment Alert", f"Sentiment for {alert['platform']} has shifted to {alert['total_sentiment']} which is outside the range of {alert['alert_range'][0]} to {alert['alert_range'][1]}")
    return {"Push Notifications Sent": len(results_within_range)}


def send_alerts_email_notifications(db: MongoClient, alerts_within_range: List[Dict], recipient_email: str) -> Dict[str, int]:
    total_email_sent = 0
    for alert in alerts_within_range:
        subject = "Product Sentiment Alert"
        body = f"Product {alert['identified_product_name']} has a total sentiment score of {alert['total_sentiment_score']} which is outside the range of {alert['alert_range'][0]} to {alert['alert_range'][1]}"
        for email in get_mail_list(db):
            send_email(subject, body, email)
            total_email_sent += 1
    return {"Email Notifications Sent": total_email_sent}


def send_sentiment_shift_email_notifications(db: MongoClient, results_within_range: List[Dict], recipient_email: str) -> Dict[str, int]:
    total_email_sent = 0
    for alert in results_within_range:
        subject = "Platform Sentiment Alert"
        body = f"Sentiment for {alert['platform']} has shifted to {alert['total_sentiment']} which is outside the range of {alert['alert_range'][0]} to {alert['alert_range'][1]}"
        for email in get_mail_list(db):
            send_email(subject, body, email)
            total_email_sent += 1
    return {"Email Notifications Sent": total_email_sent}
