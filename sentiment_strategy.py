from typing import Tuple, List
from alpaca_trade_api import REST
from lumibot.strategies.strategy import Strategy
from timedelta import Timedelta
from get_sentiment_and_news import GetSentimentAndNewsCached
import numpy as np


class SentimentStrategy(Strategy):
    """
    A trading strategy that makes decisions based on news sentiment and adjusts for market volatility and risk.
    """

    def initialize(
        self,
        symbol: str,
        get_sentiment_and_news_cached: GetSentimentAndNewsCached,
        cash_at_risk: float = 0.5,
        sleeptime: str = "24H",
        days_prior_for_news: int = 3,
        positive_sentiment_threshold: float = 0.999,
        negative_sentiment_threshold: float = 0.999,
        buy_take_profit_multiplier: float = 1.10,
        buy_stop_loss_multiplier: float = 0.97,
        sell_take_profit_multiplier: float = 0.9,
        sell_stop_loss_multiplier: float = 1.03,
        volatility_threshold: float = 0.03,
        volatility_period: int = 14,
    ):
        self.last_trade = None
        self.number_of_news = 0
        self.number_of_news_calls = 0

        self.symbol = symbol
        self.sleeptime = sleeptime
        self.cash_at_risk = cash_at_risk
        self.days_prior_for_news = days_prior_for_news
        self.get_sentiment_and_news_cached = get_sentiment_and_news_cached

        self.positive_sentiment_threshold = positive_sentiment_threshold
        self.negative_sentiment_threshold = negative_sentiment_threshold
        self.buy_take_profit_multiplier = buy_take_profit_multiplier
        self.buy_stop_loss_multiplier = buy_stop_loss_multiplier
        self.sell_take_profit_multiplier = sell_take_profit_multiplier
        self.sell_stop_loss_multiplier = sell_stop_loss_multiplier
        self.volatility_threshold = volatility_threshold
        self.volatility_period = volatility_period

    def on_trading_iteration(self):
        cash, last_price, quantity, volatility = self._position_sizing()
        probability, sentiment = self._get_sentiment()

        if cash <= last_price:
            return

        if volatility > self.volatility_threshold:
            return

        if self._should_buy(sentiment, probability):
            self._execute_buy_order(quantity, last_price)
        elif self._should_sell(sentiment, probability):
            self._execute_sell_order(quantity, last_price)

    def on_strategy_end(self):
        print(
            f"\n\nMoyenne d'articles par jour: {self._get_average_number_of_news()}\n\n"
        )

    def _position_sizing(self) -> Tuple[float, float, int, float]:
        """Calculate the position size based on available cash, risk, and volatility."""
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)

        volatility = self._get_volatility()

        adjusted_cash_at_risk = self.cash_at_risk / (1 + volatility)
        quantity = round(cash * adjusted_cash_at_risk / last_price, 0)
        return cash, last_price, quantity, volatility

    def _get_volatility(self) -> float:
        """Calculate the volatility of the asset over the past 'volatility_period' days."""
        bars = self.get_historical_prices(self.symbol, self.volatility_period, "day")

        closing_prices = bars.df["close"]
        returns = np.diff(np.log(closing_prices))
        return np.std(returns)

    def _get_sentiment(self) -> Tuple[float, str]:
        """Get the sentiment of news headlines for a specific symbol."""
        _, probability, sentiment, number_of_news = (
            self.get_sentiment_and_news_cached.get_news_and_sentiment(
                self._get_new_date_interval()
            )
        )
        self.number_of_news += number_of_news
        self.number_of_news_calls += 1
        return probability, sentiment

    def _get_new_date_interval(self) -> Tuple[str, str]:
        """Get the current date and the date X days prior."""
        today = self.get_datetime()
        days_prior_date = today - Timedelta(days=self.days_prior_for_news)
        return today.strftime("%Y-%m-%d"), days_prior_date.strftime("%Y-%m-%d")

    def _should_buy(self, sentiment: str, probability: float) -> bool:
        """Determine if a buy order should be placed."""
        return (
            sentiment == "positive" and probability > self.positive_sentiment_threshold
        )

    def _should_sell(self, sentiment: str, probability: float) -> bool:
        """Determine if a sell order should be placed."""
        return (
            sentiment == "negative" and probability > self.negative_sentiment_threshold
        )

    def _execute_buy_order(self, quantity: int, last_price: float):
        """Execute a buy order with volatility-adjusted risk management."""
        if self.last_trade == "sell":
            self.sell_all()

        order = self.create_order(
            self.symbol,
            quantity,
            "buy",
            type="bracket",
            take_profit_price=last_price * self.buy_take_profit_multiplier,
            stop_loss_price=last_price * self.buy_stop_loss_multiplier,
        )
        self.submit_order(order)
        self.last_trade = "buy"

    def _execute_sell_order(self, quantity: int, last_price: float):
        """Execute a sell order with volatility-adjusted risk management."""
        if self.last_trade == "buy":
            self.sell_all()

        order = self.create_order(
            self.symbol,
            quantity,
            "sell",
            type="bracket",
            take_profit_price=last_price * self.sell_take_profit_multiplier,
            stop_loss_price=last_price * self.sell_stop_loss_multiplier,
        )
        self.submit_order(order)
        self.last_trade = "sell"

    def _get_average_number_of_news(self) -> float:
        """Get the average number of news per day."""
        if self.number_of_news_calls <= 0:
            return None
        return self.number_of_news / self.number_of_news_calls
