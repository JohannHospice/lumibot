from alpaca_trade_api import REST
from strategies.strategies import STRATEGIES
from utils.broker_fees import BROKER_FEES
from lumibot.brokers import Alpaca, Broker
from lumibot.strategies.strategy import Strategy

import pandas as pd
from lumibot.backtesting import BacktestingBroker, PandasDataBacktesting
from lumibot.entities import Asset, Data
from lumibot.strategies import Strategy
import yfinance as yf


def build_parameters(args: dict, credentials: dict) -> dict:
    """Builds the parameters dictionary for the strategy."""
    return {
        "get_news": REST(
            base_url=credentials["BASE_URL"],
            key_id=credentials["API_KEY"],
            secret_key=credentials["API_SECRET"],
        ).get_news,
        "symbols": ["SPY", "QQQ", "DIA", "AAPL"],
        "sleeptime": args.sleeptime,
        "days_prior_for_news": args.days_prior,
        "news_limit": args.news_limit,
        "cash_at_risk": args.cash_at_risk,
        "sentiment_threshold": args.sentiment_threshold,
        "buy_take_profit_multiplier": 1 + args.take_profit_threshold,
        "buy_stop_loss_multiplier": 1 - args.stop_loss_threshold,
        "sell_take_profit_multiplier": 1 - args.take_profit_threshold,
        "sell_stop_loss_multiplier": 1 + args.stop_loss_threshold,
        "volatility_threshold": args.volatility_threshold,
        "volatility_period": args.volatility_period,
    }


def create_broker(credentials: dict) -> Broker:
    """Creates and returns an Alpaca broker instance."""
    return Alpaca(
        {
            "API_KEY": credentials["API_KEY"],
            "API_SECRET": credentials["API_SECRET"],
            "PAPER": credentials["PAPER"],
        }
    )


def create_strategy(strategy_name: str, broker: Broker, parameters: dict) -> Strategy:
    """Creates a strategy instance based on the given name."""
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    StrategyClass = STRATEGIES[strategy_name]
    return StrategyClass(name=strategy_name, broker=broker, parameters=parameters)


def create_trading_fees(args: dict):
    """Creates a dictionary of trading fees based on the given arguments."""
    if args.fees not in BROKER_FEES:
        raise ValueError(f"Unknown fees: {args.fees}")
    return BROKER_FEES.get(args.fees, {})


def get_symbol_data(symbol: str, period: str = "5d", interval: str = "1m"):
    filename = f"cache/data/{symbol}_{period}_{interval}.csv"
    try:
        df = pd.read_csv(filename)
    except Exception:
        # Download minute data from 2018 to now forf {symbol}
        data = yf.download(symbol, period=period, interval=interval)

        print(filename)
        # Save the data to a CSV file
        data.to_csv(filename)
        df = pd.read_csv(filename)

    asset = Asset(
        symbol=symbol,
        asset_type=Asset.AssetType.STOCK,
    )
    pandas_data = {}
    pandas_data[asset] = Data(
        asset,
        df,
        timestep="minute",
    )
    backtesting_start = pandas_data[asset].datetime_start
    backtesting_end = pandas_data[asset].datetime_end

    return pandas_data, backtesting_start, backtesting_end
