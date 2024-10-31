"""
# Définir la stratégie
class MovingAverageCrossStrategy(bt.Strategy):
    params = (
        ("short_period", 20),
        ("long_period", 50),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.long_period
        )
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def next(self):
        if self.crossover > 0:
            # Signal d'achat
            self.buy()
        elif self.crossover < 0:
            # Signal de vente
            self.sell()


# Définir la stratégie
class MeanReversionStrategy(bt.Strategy):
    params = (
        ("rsi_period", 14),
        ("rsi_overbought", 70),
        ("rsi_oversold", 30),
        ("bbands_period", 20),
        ("bbands_dev", 2),
    )

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)
        self.bbands = bt.indicators.BollingerBands(
            period=self.params.bbands_period, devfactor=self.params.bbands_dev
        )

    def next(self):
        if (
            self.rsi < self.params.rsi_oversold
            and self.data.close < self.bbands.lines.bot
        ):
            # Conditions d'achat
            self.buy()

        elif (
            self.rsi > self.params.rsi_overbought
            and self.data.close > self.bbands.lines.top
        ):
            # Conditions de vente
            self.sell()


class BuyHoldStrategy(bt.Strategy):

    def next(self):
        if self.position.size == 0:
            amount_to_invest = 0.95 * self.broker.getcash()
            size = math.floor(amount_to_invest / self.data)
            print("Buy {} shares at {}".format(size, self.data.close[0]))
            self.buy(size=size)


class GoldenCrossStrategy(bt.Strategy):
    params = (("sma_50", 50), ("sma_200", 200), ("order_percentage", 0.95))

    def __init__(self):
        # Create 50 SMA
        self.sma_moving_average_50 = bt.indicators.SMA(
            self.data.close, period=self.params.sma_50, plotname="50 day moving average"
        )

        # Create 200 SMA
        self.sma_moving_average_200 = bt.indicators.SMA(
            self.data.close,
            period=self.params.sma_200,
            plotname="200 day moving average",
        )

        # Create crossover using the SMA's
        self.crossover = bt.indicators.CrossOver(
            self.sma_moving_average_50, self.sma_moving_average_200
        )

    def next(self):

        # Open trade
        if self.position.size == 0:
            if self.crossover > 0:
                amount_to_invest = self.params.order_percentage * self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.close)

                print("Buy {} shares at {}".format(self.size, self.data.close[0]))
                self.buy(size=self.size)

        # Close trade
        if self.position.size > 0:
            if self.crossover < 0:
                print("Sell {} shares at {}".format(self.size, self.data.close[0]))
                self.close()


class EMAStrategy(bt.Strategy):
    params = (
        ("short_period", 20),
        ("long_period", 50),
    )

    def __init__(self):
        self.short_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.long_period
        )

    def next(self):
        if self.short_ema > self.long_ema:
            # Condition d'achat pour la stratégie EMA
            self.buy()

        elif self.short_ema < self.long_ema:
            # Condition de vente pour la stratégie EMA
            self.sell()


class SMAStrategy(bt.Strategy):

    def __init__(self):
        self.sma = bt.indicators.SMA()

    def next(self):
        if not self.position and self.data > self.sma.lines.sma:
            amount_to_invest = 0.95 * self.broker.cash
            self.size = math.floor(amount_to_invest / self.data.close)

            print("Buy {} shares at {}".format(self.size, self.data.close[0]))
            self.buy(size=self.size)

        if self.position and self.data < self.sma.lines.sma:
            print("Sell {} shares at {}".format(self.size, self.data.close[0]))
            self.close()


class RMI(bt.Strategy):

    params = (("upperband", 70.0), ("lowerband", 30.0), ("order_percentage", 0.95))

    def __init__(self):
        self.rmi = bt.indicators.RMI(self.data, period=20)

    def next(self):
        if not self.position and self.rmi < self.params.lowerband:
            amount_to_invest = self.params.order_percentage * self.broker.cash
            self.size = math.floor(amount_to_invest / self.data.close)

            print("Buy {} shares at {}".format(self.size, self.data.close[0]))
            self.buy(size=self.size)

        if self.position and self.rmi > self.params.upperband:
            print("Sell {} shares at {}".format(self.size, self.data.close[0]))
            self.close()


class RSIStrategy(bt.Strategy):

    params = (("upperband", 85), ("lowerband", 25), ("order_percentage", 0.95))

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data, period=14)

    def next(self):
        if not self.position and self.rsi < self.params.lowerband:
            amount_to_invest = self.params.order_percentage * self.broker.cash
            self.size = math.floor(amount_to_invest / self.data.close)

            print("Buy {} shares at {}".format(self.size, self.data.close[0]))
            self.buy(size=self.size)

        if self.position and self.rsi > self.params.upperband:
            print("Sell {} shares at {}".format(self.size, self.data.close[0]))
            self.close()


class MACDStrategy(bt.Strategy):

    params = (("ema_12", 12), ("ema_26", 26), ("order_percentage", 0.95))

    def __init__(self):
        self.fast_ema_12 = bt.indicators.EMA(
            self.data.close, period=self.params.ema_12, plotname="12 day EMA"
        )

        self.slow_ema_26 = bt.indicators.EMA(
            self.data.close, period=self.params.ema_26, plotname="26 day EMA"
        )

        self.macd = bt.indicators.MACDHistogram(self.fast_ema_12, self.slow_ema_26)

    def next(self):
        if not self.position and self.macd > 0:
            amount_to_invest = self.params.order_percentage * self.broker.cash
            self.size = math.floor(amount_to_invest / self.data.close)

            print("Buy {} shares at {}".format(self.size, self.data.close[0]))
            self.buy(size=self.size)

        if self.position and self.macd < 0:
            print("Sell {} shares at {}".format(self.size, self.data.close[0]))
            self.close()

"""

from __future__ import absolute_import, division, print_function, unicode_literals
import pandas as pd
import backtrader as bt
from utils.credentials import load_api_credentials
from alpaca.data import (
    CryptoHistoricalDataClient,
)
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit


import backtrader as bt
import backtrader.analyzers as btanalyzers
import pyfolio as pf

from backtrader.analyzers import (
    SQN,
    TimeReturn,
    SharpeRatio,
    TradeAnalyzer,
)


class MarketMakingStrategy(bt.Strategy):
    params = (
        ("spread_percentage", 0.002),
        (
            "order_size_percentage",
            0.05,
        ),
        ("printlog", False),
    )

    def __init__(self):
        pass

    def next(self):
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)

        quantity, buy_price, sell_price = self._get_order_quantity_and_prices()

        self.buy(size=quantity, exectype=bt.Order.Limit, price=buy_price)
        self.sell(size=quantity, exectype=bt.Order.Limit, price=sell_price)

    def _get_order_quantity_and_prices(self):
        last_price = self.data.close[0]
        buy_price = last_price * (1 - self.params.spread_percentage / 2)
        sell_price = last_price * (1 + self.params.spread_percentage / 2)

        cash = self.broker.get_cash()
        order_size = cash * self.params.order_size_percentage
        self.log(
            "Cash Value %.2f$, Order Size %.2f$, Value %.2f$"
            % (cash, order_size, self.broker.getvalue()),
            doprint=True,
        )
        quantity = (order_size) / last_price

        return quantity, buy_price, sell_price

    # useless piece of shit

    def log(self, txt, dt=None, doprint=False):
        """Logging function fot this strategy"""
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

            else:  # Sell
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

    def stop(self):
        self.log("Ending Value %.2f$" % self.broker.getvalue(), doprint=True)


def fetch_data(
    symbol: str,
    fromdate: pd.Timestamp,
    todate: pd.Timestamp,
    timeframe: str | TimeFrame,
):
    # exchange = ccxt.binance(
    #     {
    #         "apiKey": "",
    #         "secret": "",
    #         # "apiKey": cred["API_KEY"],
    #         # "secret": cred["API_SECRET"],
    #         # "paper": True,
    #     }
    # )
    # exchange.set_sandbox_mode(True)

    # df = exchange.fetch_ohlcv(
    #     symbol,
    #     timeframe,
    # )
    # df = pd.DataFrame(
    #     df, columns=["timestamp", "open", "high", "low", "close", "volume"]
    # )
    # df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    # df.set_index("timestamp", inplace=True)
    # print(df)

    request = CryptoBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=timeframe,
        start=fromdate,
        end=todate,
    )
    df = CryptoHistoricalDataClient().get_crypto_bars(request).df
    timestamp = (
        df.xs(symbol, level="symbol")
        .index.to_frame(index=False)["timestamp"]
        .apply(lambda x: int(x.timestamp() * 1000))
        .to_frame()
    )
    df.index = pd.to_datetime(timestamp["timestamp"], unit="ms")
    df = pd.DataFrame(
        df, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    return bt.feeds.PandasData(dataname=df)


if __name__ == "__main__":

    config = {
        "symbol": "BTC/USD",
        "timeframe": TimeFrame(amount=5, unit=TimeFrameUnit.Minute),
        "fromdate": pd.to_datetime("2024-01-01"),
        "todate": pd.to_datetime("2024-03-01"),
    }

    cerebro = bt.Cerebro()
    cerebro.getbroker().set_cash(1000)
    cerebro.getbroker().set_shortcash(True)
    # cerebro.getbroker().setcommission(commission=2, mult=10, margin=2000)
    cerebro.adddata(
        fetch_data(
            symbol=config["symbol"],
            fromdate=config["fromdate"],
            todate=config["todate"],
            timeframe=config["timeframe"],
        )
    )
    cerebro.addstrategy(MarketMakingStrategy)
    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(SQN)
    cerebro.addanalyzer(TimeReturn, timeframe=bt.TimeFrame.Months)
    cerebro.addanalyzer(SharpeRatio, timeframe=bt.TimeFrame.Months)

    cerebro.addanalyzer(TradeAnalyzer)
    # cerebro.addwriter(bt.WriterFile, csv="args.writercsv", rounding=4)

    # Paramètres du backtest
    results = cerebro.run(
        stdstats=False,
        tradehistory=True,
        fromdate=config["fromdate"],
        todate=config["todate"],
    )

    # plot
    cerebro.plot(numfigs=1, volume=False, zdown=False)
