from prophet import Prophet
import pandas as pd

class ProphetModel:
    def __init__(self):
        self.model = Prophet()

    def fit(self, df):
        self.model.fit(df)

    def predict(self, future):
        return self.model.predict(future)


def preprocess_data(df):
    def fill_na_with_rolling_mean(series, window=3):
        return series.fillna(series.rolling(window, min_periods=1).mean())

    df['LikeCount'] = fill_na_with_rolling_mean(df['LikeCount'])
    df['CommentCount'] = fill_na_with_rolling_mean(df['CommentCount'])
    df['SentimentScore'] = fill_na_with_rolling_mean(df['SentimentScore'])
    df.fillna(0, inplace=True)
    return df