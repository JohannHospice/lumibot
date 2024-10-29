from lumibot.backtesting import PandasDataBacktesting
from strategies.fourier_transform_strategy import FourierTransformStrategy

import pandas as pd
from lumibot.backtesting import BacktestingBroker, PandasDataBacktesting
from lumibot.entities import Asset, Data
import yfinance as yf
from lumibot.traders import Trader

if __name__ == "__main__":
    symbol = "SPY"
    period = "5d"
    interval = "1m"
    filename = f"cache/data/{symbol}_{period}_{interval}.csv"

    try:
        df = pd.read_csv(filename)
    except Exception:
        # Download minute data from 2018 to now forf {symbol}
        data = yf.download(symbol, period=period, interval=interval)
        # Save the data to a CSV file
        data.to_csv(filename)

    df = pd.read_csv(filename)
    print(df.columns)
    asset = Asset(
        symbol=symbol,
        asset_type=Asset.AssetType.STOCK,
    )

    data = Data(
        asset,
        df,
        timestep="minute",
    )
    pandas_data = {asset: data}

    trader = Trader(backtest=True)
    backtesting_start = pandas_data[asset].datetime_start
    backtesting_end = pandas_data[asset].datetime_end

    data_source = PandasDataBacktesting(
        pandas_data=pandas_data,
        datetime_start=backtesting_start,
        datetime_end=backtesting_end,
    )
    broker = BacktestingBroker(data_source)
    strat = FourierTransformStrategy(
        broker=broker,
        budget=100000,
    )
    trader.add_strategy(strat)
    trader.run_all()

    # data_source = PandasDataBacktesting(
    #     PandasDataBacktesting,
    #     backtesting_start,
    #     backtesting_end,
    #     pandas_data=pandas_data,
    # )
    # broker = BacktestingBroker(data_source)
    # strategy = FourierTransformStrategy(
    #     broker=broker,
    #     budget=100000,
    # )
    # strategy.backtest()
