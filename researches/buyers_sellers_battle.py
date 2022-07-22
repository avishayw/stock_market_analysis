import pandas as pd
import statistics
import plotly.graph_objects as go
from utils.download_stock_csvs import download_stock
from os.path import dirname, abspath
from pathlib import Path

project_path = dirname(dirname(abspath(__file__)))

ticker = 'GOOGL'
stock_df = pd.read_csv(download_stock(ticker))

# Some statistics
stock_df["close_open_gap_percentage"] = ((stock_df["Close"] - stock_df["Open"])/stock_df["Open"])*100.0
stock_df[["Date","Volume", "close_open_gap_percentage"]].to_csv(Path(project_path, f"results/{ticker}_open_close_gap.csv"))
