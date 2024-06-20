# app/services/sentiment_analysis.py

import boto3
from app.core.config import AWS_KEY_ID, AWS_SECRET_KEY, REGION_NAME

def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of the given text
    :param text: text to analyze
    :return: sentiment of the text
    """
    comprehend = boto3.client(service_name='comprehend', aws_access_key_id=AWS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_KEY,
                              region_name=REGION_NAME)
    response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    score = response_to_score(response)
    return score


def response_to_score(response: dict) -> float:
    """
    Convert response to a single score
    :param response: response from the sentiment analysis
    :return: score of the sentiment
    """
    sentiment = response.get('SentimentScore')
    if sentiment is None:
        raise ValueError("Sentiment not found in response")
    positive = sentiment.get('Positive')
    negative = sentiment.get('Negative')
    # Neutral and Mixed are said to have a score of 0. Hence they do not affect the score
    # Furthermore positive + negative + (neutral + mixed) = 1. Hence when we give positive and negative
    # we are essentially supplying the (neutral + mixed) value as well as they just add up to 1

    # we consider positive, negative to be weights of +1 and -1 respectively
    # more positive weight, less negative weight -> near +1 score
    # more negative weight, less positive weight -> near -1 score
    # positive weight ~= negative weight -> near 0 score
    #   if positive & negative near 0 -> neutral high (in aws response), mixed low
    #   if positive & negative near 0 -> neutral low (in aws response), mixed high

    sentiment_score = positive - negative   # = (+1 * positive) + (-1 * negative)
    return sentiment_score

