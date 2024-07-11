# app\services\forecast_service.py

import pandas as pd
from app.models.prophet_model import ProphetModel, preprocess_data


async def generate_forecast(db) -> list:
    product_forecast = []

    df = pd.read_csv('app/models/data.csv')

    grouped = df.groupby('Product')
    product_datasets = {product_name: group_df for product_name, group_df in grouped}

    for product_name, group_df in product_datasets.items():
        if 'Date' in group_df.columns:
            group_df['Date'] = pd.to_datetime(group_df["Date"])
            group_df.set_index('Date', inplace=True)

        group_df = preprocess_data(group_df)
        group_df.reset_index(inplace=True)

        temp_df = group_df[['Date', 'SentimentScore', 'LikeCount', 'CommentCount']].rename(columns={'Date': 'ds', 'SentimentScore': 'y'})

        m = ProphetModel()
        m.model.add_regressor('LikeCount')
        m.model.add_regressor('CommentCount')
        m.fit(temp_df)

        future = m.model.make_future_dataframe(periods=3)
        future = future.merge(group_df[['Date', 'LikeCount', 'CommentCount']], left_on='ds', right_on='Date', how='left')
        future.drop(columns=['Date'], inplace=True)

        future['LikeCount'].fillna(future['LikeCount'].mean(), inplace=True)
        future['CommentCount'].fillna(future['CommentCount'].mean(), inplace=True)

        forecast = m.predict(future)
        forecast = forecast[['ds', 'yhat']].tail(3).reset_index(drop=True)

        latest_value = forecast['yhat'].iloc[-1]
        previous_value = forecast['yhat'].iloc[-2]
        percentage_change = ((latest_value - previous_value) / previous_value) * 100
        is_up_trend = latest_value > previous_value

        product_forecast.append({
            "product": product_name,
            "percentage": f"{percentage_change:.2f}%",
            "isUpTrend": bool(is_up_trend)
        })

    return product_forecast