from lumibot.backtesting import YahooDataBacktesting
from utils.credentials import load_api_credentials
from lumibot.brokers import Alpaca
from lumibot.traders import Trader
from strategies.market_making_strategy import MarketMakingStrategy
from datetime import datetime
import sys

if __name__ == "__main__":
    mode = sys.argv[1]
    symbol = sys.argv[2]

    credentials = load_api_credentials()
    alpaca = Alpaca(
        {
            "API_KEY": credentials["API_KEY"],
            "API_SECRET": credentials["API_SECRET"],
            "PAPER": credentials["PAPER"],
        }
    )
    strategy = MarketMakingStrategy(
        broker=alpaca,
        parameters={
            "symbol": symbol,
        },
    )

    if len(sys.argv) > 1 and mode == "backtest":
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2020, 1, 10)
        strategy.backtest(
            YahooDataBacktesting,
            backtesting_start=start_date,
            backtesting_end=end_date,
            parameters=strategy.parameters,
        )
    else:
        trader = Trader()
        trader.add_strategy(
            strategy,
        )
        trader.run_all()
