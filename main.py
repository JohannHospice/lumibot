from argument_parser import parse_arguments
from datetime import datetime
from constants import BROKER_FEES
from sentiment_strategy import SentimentStrategy
from lumibot.brokers import Broker, Alpaca
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from lumibot.backtesting import YahooDataBacktesting
from alpaca.trading import GetAssetsRequest
from credentials import load_api_credentials
from alpaca_trade_api import REST


def run(strategy: Strategy):
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()


def backtest(
    strategy: Strategy,
    start_date: datetime,
    end_date: datetime,
    parameters: dict,
    trading_fees: dict,
):
    strategy.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
        parameters=parameters,
        buy_trading_fees=trading_fees.get("buy_trading_fees", []),
        sell_trading_fees=trading_fees.get("sell_trading_fees", []),
    )


def list_assets(broker: Broker, asset_class: str):
    for asset in broker.api.get_all_assets(
        filter=GetAssetsRequest(asset_class=asset_class)
    ):
        print(f"{asset.symbol} - {asset.name} - {asset.exchange} - {asset.asset_class}")


if __name__ == "__main__":
    API_KEY, API_SECRET, PAPER, BASE_URL = load_api_credentials()

    parser, args = parse_arguments()

    broker = Alpaca({"API_KEY": API_KEY, "API_SECRET": API_SECRET, "PAPER": PAPER})

    if args.mode == "list":
        list_assets(broker, args.asset_class)

    parameters = {
        "symbol": args.symbol,
        "cash_at_risk": args.cash_at_risk,
        "sleeptime": args.sleeptime,
        "days_prior": args.days_prior,
        "news_limit": args.news_limit,
        "api": REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET),
    }
    strategy = SentimentStrategy(
        name="sentiment_strategy", broker=broker, parameters=parameters
    )

    if args.mode == "run":
        run(strategy)
    elif args.mode == "backtest":
        backtest(
            trading_fees=BROKER_FEES.get(args.fees, {}),
            strategy=strategy,
            parameters=parameters,
            start_date=args.start_date,
            end_date=args.end_date,
        )
    else:
        parser.print_help()
