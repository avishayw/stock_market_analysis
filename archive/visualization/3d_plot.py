import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import numpy as np
import pandas as pd

# fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

trades_csv = r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\results\‏‏ma_roc_er_trading_v4_in_sample_tickers_day_timeframe_copy.csv"

df = pd.read_csv(trades_csv).dropna()
backup_df = df.copy()
# print(len(df.loc[(df['stock_linear_roc_50'] >= 2.5) & df['win']])/len(df.loc[df['stock_linear_roc_50'] >= 2.5]))
# print(len(df.loc[(df['stock_linear_roc_50'] < 2.5) & df['win']])/len(df.loc[df['stock_linear_roc_50'] < 2.5]))

# df['win_numeric'] = np.where(df['win'], 1, 0)
# df['days'] = (pd.to_datetime(df['exit_date']) - pd.to_datetime(df['enter_date'])).dt.days
# df['days_to_max'] = (pd.to_datetime(df['exit_date']) - pd.to_datetime(df['period_min_date'])).dt.days
score_max = 1.0
score_min = 0.1
df = df.loc[(df['stock_linear_score_20'] <= score_max) &
            (df['stock_linear_score_20'] >= score_min) &
            (df['stock_linear_score_50'] <= score_max) &
            (df['stock_linear_score_50'] >= score_min)]
# roc_max = 1000.0
# roc_min = 0.0
# df = df.loc[(df['stock_linear_roc_20'] <= roc_max) &
#             (df['stock_linear_roc_20'] >= roc_min) &
#             (df['stock_linear_roc_50'] <= roc_max) &
#             (df['stock_linear_roc_50'] >= roc_min)]
print('win rate', len(df.loc[df['win']])/len(df))
print(len(df)/len(backup_df))
print(len(df))

threedee = plt.figure().gca(projection='3d')
threedee.scatter(df['stock_linear_roc_20'], df['stock_linear_roc_50'], df['change%'])
threedee.set_xlabel('Stock Regression ROC 20')
threedee.set_ylabel('Stock Regression ROC 50')
# threedee.scatter(df['stock_linear_score_20'], df['stock_linear_score_50'], df['change%'])
# threedee.set_xlabel('Stock Regression Score 20')
# threedee.set_ylabel('Stock Regression Score 50')
threedee.set_zlabel('Change %')
plt.show()


# plt.scatter(df['days_to_max'], df['win_numeric'])
# plt.show()

# # Make data.
# X = df['stock_linear_roc_20'].to_numpy()
# Y = df['stock_linear_score_20'].to_numpy()
# X, Y = np.meshgrid(X, Y)
# R = np.sqrt(X**2 + Y**2)
# # Z = df['win_numeric'].to_numpy()
# Z = np.sin(R)
# # Plot the surface.
# surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
#                        linewidth=0, antialiased=False)
#
# # Customize the z axis.
# # ax.set_zlim(-1.01, 1.01)
# ax.zaxis.set_major_locator(LinearLocator(10))
# # A StrMethodFormatter is used automatically
# ax.zaxis.set_major_formatter('{x:.02f}')
#
# # Add a color bar which maps values to colors.
# fig.colorbar(surf, shrink=0.5, aspect=5)
#
# plt.show()