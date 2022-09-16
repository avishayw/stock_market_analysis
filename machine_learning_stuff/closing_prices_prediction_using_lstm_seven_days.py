# Copied from https://www.kaggle.com/code/faressayah/stock-market-analysis-prediction-using-lstm/notebook
from utils.get_all_stocks import get_all_nasdaq_100_stocks
from utils.download_stock_csvs import download_stock_day, download_stock_week
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


ticker = 'QQQ'

# Get the stock quote
try:
    df = pd.read_csv(download_stock_day(ticker))
except ValueError as e:
    print(e)
    exit()

df.dropna(axis=0, inplace=True)

df.set_index('Date')
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
training_data_len = int(np.ceil( len(dataset) * .9 )) # Changed from .95 to .9

# Changing training_data_len to full df so I will have prediction for a week
# training_data_len = len(df)
# print(training_data_len)

# Scale the data
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

############# Creating the model ##############################
# # Create the training data set
# # Create the scaled training data set
# train_data = scaled_data[0:int(training_data_len), :]
#
# # Split the data into x_train and y_train data sets
# x_train = []
# y_train = []
#
# for i in range(120, len(train_data)):
#     x_train.append(train_data[i - 120:i, 0])
#     y_train.append(train_data[i-2: i, 0])
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
#
# # Build the LSTM model
# model = Sequential()
# model.add(LSTM(128, return_sequences=True, input_shape= (x_train.shape[1], 1)))
# model.add(LSTM(64, return_sequences=False))
# model.add(Dense(25))
# model.add(Dense(2))
#
# # Compile the model
# model.compile(optimizer='adam', loss='mean_squared_error')
#
# # Train the model
# model.fit(x_train, y_train, batch_size=1, epochs=1)
#
# model.save(fr"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\models\QQQ_lstm_x_120_y_2_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.h5")
#######################################################################################

# Load the saved model
model = load_model(r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\models\QQQ_lstm_x_120_y_2_2022-08-23-23-53.h5")

# Create the testing data set
# Create a new array containing scaled values from index 1543 to 2002
# TODO: remove prints
print(f'len dataset: {len(dataset)}')
print(f'shape dataset: {dataset.shape}')
print(f'len scaled data: {len(scaled_data)}')
print(f'shape scaled data: {scaled_data.shape}')
print(f'trainin_data_len: {training_data_len}')

test_data = scaled_data[training_data_len - 120:-2, :]
# TODO: remove prints
print(f'len test data: {len(test_data)}')
print(f'shape test data: {test_data.shape}')

# Create the data sets x_test and y_test
x_test = []
# y_test = dataset[training_data_len:, :]
y_test = []
for i in range(120, len(test_data)):
    x_test.append(test_data[i - 120:i, 0])
for i in range(training_data_len, len(df)-2):
    y_test.append(dataset[i:i + 2, 0])

# TODO: remove prints
print(f'len y_test: {len(y_test)}')
# Convert the data to a numpy array
x_test = np.array(x_test)
# TODO: remove prints
print(f'len x_test: {len(x_test)}')
print(f'shape x_test: {x_test.shape}')

# Reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# Get the models predicted price values
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)
# TODO: remove prints
print(predictions)

# Get the root mean squared error (RMSE)
rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))
print(rmse)

# Plot the data
for i in range(len(y_test)):
    # train = data[:training_data_len]
    valid = data[training_data_len+i:training_data_len+i+2]
    valid['Predictions'] = predictions[i]
    # Visualize the data
    plt.figure(figsize=(16,6))
    plt.title('Model')
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Close Price USD ($)', fontsize=18)
    # plt.plot(train['Close'])
    plt.plot(valid[['Close', 'Predictions']])
    plt.legend(['Val', 'Predictions'], loc='lower right')
    plt.show()

# Show the valid and predicted prices
# print(valid)
