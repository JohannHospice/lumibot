import argparse
from datetime import datetime, timezone, time
from constants import BROKER_FEES


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run or backtest SentimentStrategy")
    subparsers = parser.add_subparsers(dest="mode", help="Choose mode: run or backtest")

    run_parser = subparsers.add_parser("run", help="Run the strategy live")
    run_parser.add_argument("symbol", type=str, help="Stock symbol to trade")
    run_parser.add_argument(
        "-c",
        "--cash_at_risk",
        type=float,
        default=0.5,
        help="Fraction of cash to risk on each trade (default: 0.5)",
    )
    run_parser.add_argument(
        "-s",
        "--sleeptime",
        type=str,
        default="24H",
        help="Time to sleep between trading iterations (default: 24H)",
    )
    run_parser.add_argument(
        "-d",
        "--days_prior",
        type=int,
        default=3,
        help="Number of days prior for news analysis (default: 3)",
    )

    list_parser = subparsers.add_parser("list", help="List available assets")
    list_parser.add_argument(
        "-c",
        "--asset_class",
        type=str,
        choices=["us_equity", "crypto"],
        default="us_equity",
        help="Type of assets to list (default: us_equity)",
    )

    backtest_parser = subparsers.add_parser(
        "backtest", help="Run a backtest for the strategy"
    )
    backtest_parser.add_argument("symbol", type=str, help="Stock symbol to trade")
    backtest_parser.add_argument(
        "-c",
        "--cash_at_risk",
        type=float,
        default=0.5,
        help="Fraction of cash to risk on each trade (default: 0.5)",
    )
    backtest_parser.add_argument(
        "-s",
        "--sleeptime",
        type=str,
        default="24H",
        help="Time to sleep between trading iterations (default: 24H)",
    )
    backtest_parser.add_argument(
        "-d",
        "--days_prior",
        type=int,
        default=3,
        help="Number of days prior for news analysis (default: 3)",
    )
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
