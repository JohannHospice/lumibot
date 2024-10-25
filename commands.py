from datetime import datetime
from lumibot.brokers import Broker
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from lumibot.backtesting import YahooDataBacktesting
from alpaca.trading import GetAssetsRequest


def run_strategy(strategy: Strategy):
    """Runs the given strategy using a Trader instance."""
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()


def backtest_strategy(
    strategy: Strategy,
    start_date: datetime,
    end_date: datetime,
    parameters: dict,
    trading_fees: dict,
):
    """Backtests the given strategy over a specified date range."""
    strategy.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
        parameters=parameters,
        buy_trading_fees=trading_fees.get("buy_trading_fees", []),
        sell_trading_fees=trading_fees.get("sell_trading_fees", []),
    )


def list_assets(broker: Broker, asset_class: str):
    """Lists all assets of a given class from the broker."""
    for asset in broker.api.get_all_assets(
        filter=GetAssetsRequest(asset_class=asset_class)
    ):
        print(f"{asset.symbol} - {asset.name} - {asset.exchange} - {asset.asset_class}")
