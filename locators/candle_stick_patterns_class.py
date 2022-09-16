import pandas as pd
import numpy as np
from locators import candle_stick_patterns
from locators.trends import successive_trends_detector


class CandlestickPatterns():

    def __init__(self, df):
        self.df = pd.DataFrame.copy(df)
        self.patterns()
        self.trends()
        self.bullish_patterns()
        self.bearish_patterns()

    def patterns(self):
        self.df = candle_stick_patterns.doji(self.df)
        self.df = candle_stick_patterns.long_legged_doji(self.df)
        self.df = candle_stick_patterns.dragonfly_doji(self.df)
        self.df = candle_stick_patterns.gravestone_doji(self.df)
        self.df = candle_stick_patterns.hanging_man(self.df)
        self.df = candle_stick_patterns.hammer(self.df)
        self.df = candle_stick_patterns.shooting_star(self.df)
        self.df = candle_stick_patterns.inverted_hammer(self.df)
        self.df = candle_stick_patterns.bullish_engulfing(self.df)
        self.df = candle_stick_patterns.bearish_engulfing(self.df)
        self.df = candle_stick_patterns.dark_cloud_cover(self.df)
        self.df = candle_stick_patterns.bullish_piercing(self.df)
        self.df = candle_stick_patterns.bearish_piercing(self.df)
        self.df = candle_stick_patterns.evening_doji_star(self.df)
        self.df = candle_stick_patterns.evening_star(self.df)
        self.df = candle_stick_patterns.morning_doji_star(self.df)
        self.df = candle_stick_patterns.morning_star(self.df)
        self.df = candle_stick_patterns.spinning_top(self.df)

    def trends(self):
        self.df = successive_trends_detector(self.df)

    def bullish_patterns(self):
        self.df['bullish_patterns'] = np.where(
            (self.df['doji']) |
            (self.df['long_legged_doji']) |
            (self.df['dragonfly_doji']) |
            (self.df['hammer']) |
            (self.df['inverted_hammer']) |
            (self.df['bearish_engulfing']) |
            (self.df['bearish_piercing']) |
            (self.df['morning_star']) |
            (self.df['morning_doji_star']), True, False
        )

    def bearish_patterns(self):
        self.df['bearish_patterns'] = np.where(
            (self.df['doji']) |
            (self.df['long_legged_doji']) |
            (self.df['gravestone_doji']) |
            (self.df['hanging_man']) |
            (self.df['shooting_star']) |
            (self.df['bullish_engulfing']) |
            (self.df['bullish_piercing']) |
            (self.df['evening_star']) |
            (self.df['evening_doji_star']), True, False
        )

