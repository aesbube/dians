from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from keras.api.models import Sequential
from keras.api.layers import LSTM, Dense
import keras

class lstm_model:
    def __init__(self, data):
        self.data = data
    
    """ Used to parse the format of the data from the API response """
    def parse_singular(self, entry: str):
        return int(entry[:-8].replace('.', ''))

    """ Parses the data from the API response to a more readable format """
    def parse_data(self):
        data_copy = []
        for entry in self.data:
            parsed = dict()
            parsed['date'] = entry['date']
            for part in ['last_transaction', 'max_value', 'min_value']:
                parsed[part] = self.parse_singular(entry[part])
            parsed["volume"] = int(entry["volume"][:].replace('.', ''))
            data_copy.append(parsed)
        return data_copy


    """ The main function that predicts the stock prices, given the data """
    def predictor(self):
        data = self.parse_data()
        data = pd.DataFrame(data=data)
        
        """ Removing unnecessary columns, reversing the data and setting the date as the index """
        data.drop(columns=['min_value', 'max_value', 'volume'], inplace=True)
        data['date'] = pd.to_datetime(data['date'], dayfirst=True)
        data = data[::-1]
        data.set_index('date', inplace=True)

        """ If the data is too small, return a forecast of the last transaction """
        if len(data) < 50:
            forecast = [int(data['last_transaction'][-1])] * 10
            forecast_start_date = datetime.today()
            forecast_dates = [date.strftime("%d.%m.%Y") for date in pd.date_range(
                start=forecast_start_date, periods=10).tolist()]
            return {"forecast": forecast, "forecast_dates": forecast_dates, "dates": [datetime.strftime(date, "%d.%m.%Y") for date in data.index],
                    "prices": data['last_transaction'].tolist()}

        lag = 5
        periods = range(lag, 0, -1)
        data = pd.concat([data, data.shift(periods=periods)], axis=1)

        data.dropna(axis=0, inplace=True)
        
        """ Splitting the data into training and testing sets """
        x, y = data.drop(columns=['last_transaction']), data['last_transaction']
        train_x, test_x, train_y, test_y = train_test_split(
            x, y, test_size=0.3, shuffle=False)

        train_x = train_x.values.reshape(
            train_x.shape[0], lag, (train_x.shape[1] // lag))
        test_x = test_x.values.reshape(
            test_x.shape[0], lag, (test_x.shape[1] // lag))

        """ Building and training the LSTM model """
        model = Sequential()
        model.add(LSTM(100,  activation='relu', input_shape=(
            train_x.shape[1], train_x.shape[2]), return_sequences=True))
        model.add(LSTM(50,  activation='relu'))
        model.add(Dense(1, activation='linear'))

        model.compile(loss=keras.losses.MeanSquaredError(), optimizer=keras.optimizers.Adam(
        ), metrics=[keras.metrics.MeanSquaredError(), keras.metrics.MeanAbsoluteError()])

        history = model.fit(train_x, train_y, batch_size=16,
                            validation_split=0.2, epochs=5, shuffle=False)

        """ Predicting the stock prices """
        preds = model.predict(test_x)

        look_back = lag
        to_predict = test_x[-look_back]

        def predict(num_prediction, model):
            prediction_list = to_predict[-look_back:]

            for _ in range(num_prediction):
                pred = prediction_list[-look_back:]
                pred = pred.reshape((1, look_back, 1))
                out = model.predict(pred)[0][0]
                prediction_list = np.append(prediction_list, out)
            prediction_list = prediction_list[look_back-1:]

            return prediction_list

        def predict_dates(num_prediction):
            last_date = datetime.today()
            prediction_dates = pd.date_range(
                last_date, periods=num_prediction+1).tolist()
            return prediction_dates

        num_prediction = 9
        forecast = predict(num_prediction, model)
        forecast_dates = predict_dates(num_prediction)

        forecast = [int(x) for x in forecast]

        forecast_dates = [datetime.strftime(pd.to_datetime(
            date), "%d.%m.%Y") for date in forecast_dates]

        dates = [datetime.strftime(date, "%d.%m.%Y") for date in data.index[-min(500, len(data.index)):]]
        
        prices = data['last_transaction'].tolist()[-min(500, len(data['last_transaction'])):]
        
        return {"forecast": forecast, "forecast_dates": forecast_dates, "dates": dates, "prices": prices}
    
    def get_predictions(self):
        return self.predictor()
