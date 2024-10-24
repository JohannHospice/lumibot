from typing import Tuple

from alpaca_trade_api import REST
from lumibot.strategies.strategy import Strategy
from timedelta import Timedelta
from get_sentiment_and_news import GetSentimentAndNewsCached

# Constants
POSITIVE_SENTIMENT_THRESHOLD = 0.999
NEGATIVE_SENTIMENT_THRESHOLD = 0.999
BUY_TAKE_PROFIT_MULTIPLIER = 1.20
BUY_STOP_LOSS_MULTIPLIER = 0.95
SELL_TAKE_PROFIT_MULTIPLIER = 0.8
SELL_STOP_LOSS_MULTIPLIER = 1.05


class SentimentStrategy(Strategy):
    """
    A trading strategy that makes decisions based on news sentiment.
    """

    def initialize(
        self,
        symbol: str,
        cash_at_risk: float,
        sleeptime: str,
        api: REST,
        days_prior: int = 3,
    ):
        self.symbol = symbol
        self.sleeptime = sleeptime
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.days_prior = days_prior
        self.number_of_news = 0
        self.number_of_news_calls = 0
        self.get_sentiment_and_news_cached = GetSentimentAndNewsCached(
            symbol, api.get_news
        )

    def on_trading_iteration(self):
        cash, last_price, quantity = self._position_sizing()
        probability, sentiment = self._get_sentiment()

        if cash <= last_price:
            return

        if self._should_buy(sentiment, probability):
            self._execute_buy_order(quantity, last_price)
        elif self._should_sell(sentiment, probability):
            self._execute_sell_order(quantity, last_price)

    def on_strategy_end(self):
        print(
            f"\n\nMoyenne d'articles par jour: {self._get_average_number_of_news()}\n\n"
        )

    def _position_sizing(self) -> Tuple[float, float, int]:
        """Calculate the position size based on available cash and risk."""
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def _get_sentiment(self) -> Tuple[float, str]:
        """Get the sentiment of news headlines."""
        _, probability, sentiment, number_of_news = (
            self.get_sentiment_and_news_cached.get_news_and_sentiment(self._get_dates())
        )
        self.number_of_news = self.number_of_news + number_of_news
        self.number_of_news_calls = self.number_of_news_calls + 1
        return probability, sentiment

    def _get_dates(self) -> Tuple[str, str]:
        """Get the current date and the date X days prior."""
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=self.days_prior)
        return today.strftime("%Y-%m-%d"), three_days_prior.strftime("%Y-%m-%d")

    def _should_buy(self, sentiment: str, probability: float) -> bool:
        """Determine if a buy order should be placed."""
        return sentiment == "positive" and probability > POSITIVE_SENTIMENT_THRESHOLD

    def _should_sell(self, sentiment: str, probability: float) -> bool:
        """Determine if a sell order should be placed."""
        return sentiment == "negative" and probability > NEGATIVE_SENTIMENT_THRESHOLD

    def _execute_buy_order(self, quantity: int, last_price: float):
        """Execute a buy order."""
        if self.last_trade == "sell":
            self.sell_all()
        order = self.create_order(
            self.symbol,
            quantity,
            "buy",
            type="bracket",
            take_profit_price=last_price * BUY_TAKE_PROFIT_MULTIPLIER,
            stop_loss_price=last_price * BUY_STOP_LOSS_MULTIPLIER,
        )
        self.submit_order(order)
        self.last_trade = "buy"

    def _execute_sell_order(self, quantity: int, last_price: float):
        """Execute a sell order."""
        if self.last_trade == "buy":
            self.sell_all()
        order = self.create_order(
            self.symbol,
            quantity,
            "sell",
            type="bracket",
            take_profit_price=last_price * SELL_TAKE_PROFIT_MULTIPLIER,
            stop_loss_price=last_price * SELL_STOP_LOSS_MULTIPLIER,
        )
        self.submit_order(order)
        self.last_trade = "sell"

    def _get_average_number_of_news(self) -> float:
        """Get the average number of news per day."""
        if self.number_of_news_calls <= 0:
            return None
        return self.number_of_news / self.number_of_news_calls
