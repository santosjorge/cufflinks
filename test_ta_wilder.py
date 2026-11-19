"""cufflinks.ta.rsi / atr must equal TA-Lib's RSI and ATR (Wilder's smoothing).

Run: python -m pytest test_ta_wilder.py  (or python -m unittest test_ta_wilder)
"""
import math
import unittest

import pandas as pd

import cufflinks.ta as cta

CLOSE = [
    101.2, 100.8, 101.7, 102.0, 101.3, 102.5, 102.1, 103.0, 103.3, 102.6,
    103.8, 103.4, 104.3, 104.6, 103.9, 105.1, 104.7, 105.6, 105.9, 105.2,
    106.4, 106.0, 106.9, 107.2, 106.5, 105.4, 105.9, 105.1, 104.8, 105.4,
    104.3, 104.8, 104.0, 103.7, 104.3, 103.2, 103.7, 102.9, 102.6, 103.2,
]
HIGH = [
    101.5, 101.2, 102.2, 102.6, 101.6, 102.9, 102.6, 103.6, 103.6, 103.0,
    104.3, 104.0, 104.6, 105.0, 104.4, 105.7, 105.0, 106.0, 106.4, 105.8,
    106.7, 106.4, 107.4, 107.8, 106.8, 105.8, 106.4, 105.7, 105.1, 105.8,
    104.8, 105.4, 104.3, 104.1, 104.8, 103.8, 104.0, 103.3, 103.1, 103.8,
]
LOW = [
    100.8, 100.3, 101.1, 101.6, 100.8, 101.9, 101.7, 102.5, 102.7, 102.2,
    103.3, 102.8, 103.9, 104.1, 103.3, 104.7, 104.2, 105.0, 105.5, 104.7,
    105.8, 105.6, 106.4, 106.6, 106.1, 104.9, 105.3, 104.7, 104.3, 104.8,
    103.9, 104.3, 103.4, 103.3, 103.8, 102.6, 103.3, 102.4, 102.0, 102.8,
]


def frame():
    idx = pd.date_range("2024-01-01", periods=len(CLOSE), freq="B")
    return pd.DataFrame({"high": HIGH, "low": LOW, "close": CLOSE}, index=idx)


class WilderTest(unittest.TestCase):
    def test_rsi_matches_talib(self):
        rsi = cta.rsi(frame(), periods=14, column="close", include=False).iloc[:, 0]
        # talib.RSI(close, 14) with TA-Lib 0.6: bar 14 = 64.51612903225808, last = 45.822427428823396
        self.assertTrue(rsi.iloc[:14].isna().all())
        self.assertTrue(math.isclose(rsi.iloc[14], 64.51612903225808, rel_tol=1e-12))
        self.assertTrue(math.isclose(rsi.iloc[-1], 45.822427428823396, rel_tol=1e-12))

    def test_atr_matches_talib(self):
        atr = cta.atr(frame(), periods=14, include=False).iloc[:, 0]
        # talib.ATR(high, low, close, 14): bar 14 = 1.1999999999999997, last = 1.1830924418269704
        self.assertTrue(atr.iloc[:14].isna().all())
        self.assertTrue(math.isclose(atr.iloc[14], 1.1999999999999997, rel_tol=1e-12))
        self.assertTrue(math.isclose(atr.iloc[-1], 1.1830924418269704, rel_tol=1e-12))

    def test_detail_columns_are_the_wilder_averages(self):
        out = cta.rsi(frame(), periods=14, column="close", include=False, detail=True)
        up = out[[c for c in out.columns if "UpAvg" in c][0]]
        down = out[[c for c in out.columns if "DownAvg" in c][0]]
        rsi = out[[c for c in out.columns if c.startswith("RSI")][0]]
        self.assertTrue(math.isclose(rsi.iloc[-1], 100 - 100 / (1 + up.iloc[-1] / down.iloc[-1]), rel_tol=1e-12))

    def test_short_input_is_empty(self):
        rsi = cta.rsi(frame().iloc[:10], periods=14, column="close", include=False).iloc[:, 0]
        self.assertTrue(rsi.isna().all())


if __name__ == "__main__":
    unittest.main()
