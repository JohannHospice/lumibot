from typing import Tuple
from alpaca_trade_api import REST
from lumibot.strategies.strategy import Strategy
from timedelta import Timedelta
from sentiment.get_sentiment_and_news_cached import GetSentimentAndNewsCached
import numpy as np


class SentimentStrategy(Strategy):
    """
    A trading strategy that makes decisions based on news sentiment and adjusts for market volatility and risk.
    """

    def initialize(
        self,
        symbols: list,
        get_news: REST.get_news,
        cash_at_risk: float = 0.5,
        sleeptime: str = "24H",
        days_prior_for_news: int = 3,
        news_limit: int = 10,
        sentiment_threshold: float = 0.999,
        buy_take_profit_multiplier: float = 1.10,
        buy_stop_loss_multiplier: float = 0.97,
        sell_take_profit_multiplier: float = 0.9,
        sell_stop_loss_multiplier: float = 1.03,
        volatility_threshold: float = 0.03,
        volatility_period: int = 14,
        volatility_factor: float = 0.1,  # Ajout d'un facteur de volatilité
    ):
        self.symbols = symbols
        self.last_trade = None
        self.number_of_news = 0
        self.number_of_news_calls = 0

        self.sleeptime = sleeptime
        self.cash_at_risk = cash_at_risk
        self.days_prior_for_news = days_prior_for_news
        self.news_limit = news_limit
        self.get_news = get_news

        self.sentiment_threshold = sentiment_threshold
        self.buy_take_profit_multiplier = buy_take_profit_multiplier
        self.buy_stop_loss_multiplier = buy_stop_loss_multiplier
        self.sell_take_profit_multiplier = sell_take_profit_multiplier
        self.sell_stop_loss_multiplier = sell_stop_loss_multiplier
        self.volatility_threshold = volatility_threshold
        self.volatility_period = volatility_period
        self.volatility_factor = volatility_factor  # Ajout d'un facteur de volatilité

        print(f"Sleep time: {self.sleeptime}")
        print(f"Cash at risk: {self.cash_at_risk}")
        print(f"Days prior for news: {self.days_prior_for_news}")
        print(f"Sentiment threshold: {self.sentiment_threshold}")
        print(f"Buy take profit multiplier: {self.buy_take_profit_multiplier}")
        print(f"Buy stop loss multiplier: {self.buy_stop_loss_multiplier}")
        print(f"Sell take profit multiplier: {self.sell_take_profit_multiplier}")
        print(f"Sell stop loss multiplier: {self.sell_stop_loss_multiplier}")
        print(f"Volatility threshold: {self.volatility_threshold}")
        print(f"Volatility period: {self.volatility_period}")
        print(f"News limit: {news_limit}")

    def on_trading_iteration(self):
        for symbol in self.symbols:
            cash, last_price, quantity = self._position_sizing(symbol)
            probability, sentiment = self._get_sentiment(symbol)

            if cash <= last_price:
                return

            if sentiment == "positive" and probability > self.sentiment_threshold:
                self._execute_buy_order(symbol, quantity, last_price)
            elif sentiment == "negative" and probability > self.sentiment_threshold:
                self._execute_sell_order(symbol, quantity, last_price)

    def on_strategy_end(self):
        print(
            f"\n\nMoyenne d'articles par jour: {self._get_average_number_of_news()}\n\n"
        )

    def _position_sizing(self, symbol) -> Tuple[float, float, int, float]:
        """Calculate the position size based on available cash, risk, and volatility."""
        cash = self.get_cash()
        last_price = self.get_last_price(symbol)

        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def _get_sentiment(self, symbol) -> Tuple[float, str]:
        """Get the sentiment of news headlines for a specific symbol."""
        get_sentiment_and_news_cached = GetSentimentAndNewsCached(
            symbol,
            self.news_limit,
            self.get_news,
        )
        _, probability, sentiment, number_of_news = (
            get_sentiment_and_news_cached.get_news_and_sentiment(
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

    def _execute_buy_order(self, symbol: str, quantity: int, last_price: float):
        """Execute a buy order with dynamic take-profit and stop-loss based on volatility."""
        if self.last_trade == "sell":
            self.sell_all()

        order = self.create_order(
            symbol,
            quantity,
            "buy",
            type="bracket",
            take_profit_price=last_price * self.buy_take_profit_multiplier,
            stop_loss_price=last_price * self.buy_stop_loss_multiplier,
        )
        self.submit_order(order)
        self.last_trade = "buy"

    def _execute_sell_order(self, symbol: str, quantity: int, last_price: float):
        """Execute a sell order with dynamic take-profit and stop-loss based on volatility."""
        if self.last_trade == "buy":
            self.sell_all()

        order = self.create_order(
            symbol,
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
