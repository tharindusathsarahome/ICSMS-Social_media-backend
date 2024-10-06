from prophet import Prophet
import pandas as pd

class ProphetModel:
    """
    A class for handling time series forecasting using the Prophet model.

    Attributes:
        model (Prophet): An instance of the Prophet model for forecasting.
    """
    
    def __init__(self):
        self.model = Prophet()

    def fit(self, df):
        self.model.fit(df)

    def predict(self, future):
        return self.model.predict(future)


def preprocess_data(df):
    """
    Preprocesses the input DataFrame by filling missing values with rolling mean.

    Parameters:
        df (DataFrame): A pandas DataFrame to preprocess.
        
    Returns:
        DataFrame: The preprocessed DataFrame with missing values filled.
    """
    
    def fill_na_with_rolling_mean(series, window=3):
        return series.fillna(series.rolling(window, min_periods=1).mean())

    df['LikeCount'] = fill_na_with_rolling_mean(df['LikeCount'])
    df['CommentCount'] = fill_na_with_rolling_mean(df['CommentCount'])
    df['SentimentScore'] = fill_na_with_rolling_mean(df['SentimentScore'])
    df.fillna(0, inplace=True)
    return df