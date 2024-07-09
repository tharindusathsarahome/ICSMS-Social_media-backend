from prophet import Prophet

class ProphetModel:
    def __init__(self):
        self.model = Prophet()

    def fit(self, df):
        self.model.fit(df)

    def predict(self, future):
        return self.model.predict(future)
