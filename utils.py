from alpaca_trade_api import REST

from constants import STRATEGIES, BROKER_FEES
from lumibot.brokers import Alpaca, Broker
from lumibot.strategies.strategy import Strategy


def build_parameters(args: any, API_KEY: str, API_SECRET: str, BASE_URL: str) -> dict:
    """Builds the parameters dictionary for the strategy."""
    return {
        "get_news": REST(
            base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET
        ).get_news,
        "symbol": args.symbol,
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


def create_strategy(strategy_name: str, broker, parameters: dict) -> Strategy:
    """Creates a strategy instance based on the given name."""
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    StrategyClass = STRATEGIES[strategy_name]
    return StrategyClass(name=strategy_name, broker=broker, parameters=parameters)


def create_broker(API_KEY: str, API_SECRET: str, PAPER: bool) -> Broker:
    """Creates and returns an Alpaca broker instance."""
    return Alpaca(
        {
            "API_KEY": API_KEY,
            "API_SECRET": API_SECRET,
            "PAPER": PAPER,
        }
    )


def create_trading_fees(args):
    """Creates a dictionary of trading fees based on the given arguments."""
    if args.fees not in BROKER_FEES:
        raise ValueError(f"Unknown fees: {args.fees}")
    return BROKER_FEES.get(args.fees, {})
