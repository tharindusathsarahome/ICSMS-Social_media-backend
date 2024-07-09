# app\services\model_integration_service.py

from app.models.prophet_model import ProphetModel
import pandas as pd

def train_model(data):
    df = pd.DataFrame(data)
    model = ProphetModel()
    model.fit(df)
    return model

def make_prediction(model, periods):
    future = model.model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast
