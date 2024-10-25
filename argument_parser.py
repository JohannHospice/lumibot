import argparse
from datetime import datetime, timezone, time
from constants import BROKER_FEES


def add_common_arguments(
    parser,
    cash_default=0.5,
    sleeptime_default="24H",
    days_prior_default=3,
    news_limit_default=10,
    strategy_choices=["sentiment", "momentum"],
    strategy_default="sentiment",
    tp_default=0.3,
    sl_default=0.1,
    sentiment_thr_default=0.9,
    volatility_thr_default=0.01,
    volatility_period_default=7,
):
    parser.add_argument("symbol", type=str, help="Stock symbol to trade")
    parser.add_argument(
        "-c",
        "--cash_at_risk",
        type=float,
        default=cash_default,
        help="Fraction of cash to risk on each trade (default: {})".format(
            cash_default
        ),
    )
    parser.add_argument(
        "-s",
        "--sleeptime",
        type=str,
        default=sleeptime_default,
        help="Time to sleep between trading iterations (default: {})".format(
            sleeptime_default
        ),
    )
    parser.add_argument(
        "-d",
        "--days_prior",
        type=int,
        default=days_prior_default,
        help="Number of days prior for news analysis (default: {})".format(
            days_prior_default
        ),
    )
    parser.add_argument(
        "-nl",
        "--news_limit",
        type=int,
        default=news_limit_default,
        help="Limit of news fetched for the strategy (default: {})".format(
            news_limit_default
        ),
    )
    parser.add_argument(
        "-st",
        "--strategy",
        type=str,
        choices=strategy_choices,
        default=strategy_default,
        help="Choose the strategy to run (default: {})".format(strategy_default),
    )
    parser.add_argument(
        "-tp",
        "--take_profit_threshold",
        type=float,
        default=tp_default,
        help="Take profit threshold (default: {})".format(tp_default),
    )
    parser.add_argument(
        "-sl",
        "--stop_loss_threshold",
        type=float,
        default=sl_default,
        help="Stop loss threshold (default: {})".format(sl_default),
    )
    parser.add_argument(
        "-sthr",
        "--sentiment_threshold",
        type=float,
        default=sentiment_thr_default,
        help="Sentiment threshold for making trading decisions (default: {})".format(
            sentiment_thr_default
        ),
    )
    parser.add_argument(
        "-vt",
        "--volatility_threshold",
        type=float,
        default=volatility_thr_default,
        help="Volatility threshold for trading decisions (default: {})".format(
            volatility_thr_default
        ),
    )
    parser.add_argument(
        "-vp",
        "--volatility_period",
        type=int,
        default=volatility_period_default,
        help="Period over which to calculate volatility (default: {} days)".format(
            volatility_period_default
        ),
    )


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run or backtest SentimentStrategy")
    subparsers = parser.add_subparsers(dest="mode", help="Choose mode: run or backtest")

    # Run parser
    run_parser = subparsers.add_parser("run", help="Run the strategy live")
    add_common_arguments(run_parser)

    # List parser
    list_parser = subparsers.add_parser("list", help="List available assets")
    list_parser.add_argument(
        "-c",
        "--asset_class",
        type=str,
        choices=["us_equity", "crypto"],
        default="us_equity",
        help="Type of assets to list (default: us_equity)",
    )

    # Backtest parser
    backtest_parser = subparsers.add_parser(
        "backtest", help="Run a backtest for the strategy"
    )
    add_common_arguments(backtest_parser)
    backtest_parser.add_argument(
        "-sd",
        "--start_date",
        type=lambda s: datetime.combine(datetime.strptime(s, "%Y-%m-%d"), time.min),
        required=True,
        help="Start date for backtest (YYYY-MM-DD)",
    )
    backtest_parser.add_argument(
        "-ed",
        "--end_date",
        type=lambda s: datetime.combine(datetime.strptime(s, "%Y-%m-%d"), time.max),
        default=datetime.now(timezone.utc),
        help="End date for backtest (YYYY-MM-DD, default: current date)",
    )
    backtest_parser.add_argument(
        "-f",
        "--fees",
        type=str,
        choices=list(BROKER_FEES.keys()),
        help="Choose the broker fees model",
    )

    return parser, parser.parse_args()
