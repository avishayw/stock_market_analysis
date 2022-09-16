# Copied from https://www.kaggle.com/code/faressayah/stock-market-analysis-prediction-using-lstm/notebook
from utils.get_all_stocks import get_all_nasdaq_100_stocks
from utils.download_stock_csvs import download_stock_day
from utils.download_stock_csvs import download_stock_week
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
plt.style.use("fivethirtyeight")
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.models import load_model
from pandas_datareader.data import DataReader
import yfinance as yf
from datetime import datetime


# Get the stock quote
df = DataReader('AMD', data_source='yahoo', start='1999-06-15', end=datetime.now())
# Show the data
# print(df)

# plt.figure(figsize=(16,6))
# plt.title('Close Price History')
# plt.plot(df['Close'])
# plt.xlabel('Date', fontsize=18)
# plt.ylabel('Close Price USD ($)', fontsize=18)
# plt.show()

# Create a new dataframe with only the 'Close column
data = df.filter(['Close'])
# Convert the dataframe to a numpy array
dataset = data.values
# Get the number of rows to train the model on
training_data_len = int(np.ceil( len(dataset) * .98 ))

print(training_data_len)

# Scale the data
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

######################################### Creating the model ########################################################
# # Create the training data set
# # Create the scaled training data set
# train_data = scaled_data[0:int(training_data_len), :]
#
# # Split the data into x_train and y_train data sets
# x_train = []
# y_train = []
#
# for i in range(60, len(train_data)):
#     x_train.append(train_data[i - 60:i, 0])
#     y_train.append(train_data[i, 0])
#     # if i <= 61:
#     #     print(x_train)
#     #     print(y_train)
#     #     print()
#
# # Convert the x_train and y_train to numpy arrays
# x_train, y_train = np.array(x_train), np.array(y_train)
#
# # Reshape the data
# x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
# # x_train.shape
#
# # Build the LSTM model
# model = Sequential()
# model.add(LSTM(128, return_sequences=True, input_shape= (x_train.shape[1], 1)))
# model.add(LSTM(64, return_sequences=False))
# model.add(Dense(25))
# model.add(Dense(1))
#
# # Compile the model
# model.compile(optimizer='adam', loss='mean_squared_error')
#
# # Train the model
# model.fit(x_train, y_train, batch_size=1, epochs=1)
#
# model.save(fr"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\models\AMD_lstm_x_60_y_1_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.h5")
############################################################

model = load_model(r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\models\AMD_lstm_x_60_y_1_2022-08-24-15-52.h5")

# Create the testing data set
# # Create a new array containing scaled values from index 1543 to 2002
# test_data = scaled_data[training_data_len - 60:, :]
# # Create the data sets x_test and y_test
# x_test = []
# y_test = dataset[training_data_len:, :]
# for i in range(60, len(test_data)):
#     x_test.append(test_data[i - 60:i, 0])
#
# # Convert the data to a numpy array
# x_test = np.array(x_test)
#
# # Reshape the data
# x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
#
# # Get the models predicted price values
# predictions = model.predict(x_test)
# predictions = scaler.inverse_transform(predictions)
#
# # Get the root mean squared error (RMSE)
# rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))
# print(rmse)

days_to_predict = 10
scaled_data_for_prediction = scaled_data[-60 - days_to_predict:-days_to_predict, :]
print(scaled_data_for_prediction)
predictions = []
for i in range(days_to_predict):
    x_predict = []
    x_predict.append(scaled_data_for_prediction[-60:, 0])
    x_predict = np.array(x_predict)
    x_predict = np.reshape(x_predict, (x_predict.shape[0], x_predict.shape[1], 1))
    prediction = model.predict(x_predict)
    predictions.append(scaler.inverse_transform(prediction)[0])
    scaled_data_for_prediction = np.append(scaled_data_for_prediction, prediction, axis=0)

predictions = np.array(predictions)

# print(data[training_data_len:-5].shape)
predictions_array = np.empty(data[training_data_len:-days_to_predict].shape)
predictions_array[:] = np.nan
predictions_array = np.append(predictions_array, predictions, axis=0)
print(predictions_array)
print(len(predictions_array))

# Plot the data (OLD)
train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predictions_array.copy()
# Visualize the data
plt.figure(figsize=(16, 6))
plt.title('Model')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
plt.show()

# Plot the data (OLD)
# train = data[:training_data_len]
# valid = data[training_data_len:]
# valid['Predictions'] = predictions
# # Visualize the data
# plt.figure(figsize=(16,6))
# plt.title('Model')
# plt.xlabel('Date', fontsize=18)
# plt.ylabel('Close Price USD ($)', fontsize=18)
# plt.plot(train['Close'])
# plt.plot(valid[['Close', 'Predictions']])
# plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
# plt.show()

# Show the valid and predicted prices
# print(valid)
