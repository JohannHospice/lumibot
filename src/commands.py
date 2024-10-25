from lumibot.traders import Trader
from lumibot.backtesting import YahooDataBacktesting
from alpaca.trading import GetAssetsRequest
from utils.utils import (
    build_parameters,
    create_broker,
    create_strategy,
    create_trading_fees,
)


def run_strategy(args: dict, credentials: dict):
    """Runs the given strategy using a Trader instance."""
    broker = create_broker(credentials)
    parameters = build_parameters(args, credentials)
    strategy = create_strategy(args.strategy, broker, parameters)

    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()


def backtest_strategy(args: dict, credentials: dict):
    """Backtests the given strategy over a specified date range."""
    broker = create_broker(credentials)
    parameters = build_parameters(args, credentials)
    trading_fees = create_trading_fees(args)
    strategy = create_strategy(args.strategy, broker, parameters)

    strategy.backtest(
        YahooDataBacktesting,
        backtesting_start=args.start_date,
        backtesting_end=args.end_date,
        parameters=parameters,
        buy_trading_fees=trading_fees.get("buy_trading_fees", []),
        sell_trading_fees=trading_fees.get("sell_trading_fees", []),
    )


def list_assets(args: dict, credentials: dict):
    """Lists all assets of a given class from the broker."""
    broker = create_broker(credentials)
    for asset in broker.api.get_all_assets(
        filter=GetAssetsRequest(asset_class=args.asset_class)
    ):
        print(f"{asset.symbol} - {asset.name} - {asset.exchange} - {asset.asset_class}")
