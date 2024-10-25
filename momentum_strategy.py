from lumibot.strategies.strategy import Strategy
import numpy as np
from typing import Tuple


class MomentumStrategy(Strategy):
    """
    A simple momentum-based trend-following strategy.
    The strategy buys when the price is above the moving average (indicating upward trend)
    and sells when it is below the moving average (indicating downward trend).
    """

    def initialize(
        self,
        symbol: str,
        moving_average_period: int = 20,
        cash_at_risk: float = 0.5,
        volatility_period: int = 14,
        stop_loss_multiplier: float = 0.97,
        take_profit_multiplier: float = 1.10,
        volatility_factor: float = 0.1,
    ):
        self.symbol = symbol
        self.moving_average_period = moving_average_period
        self.cash_at_risk = cash_at_risk
        self.volatility_period = volatility_period
        self.stop_loss_multiplier = stop_loss_multiplier
        self.take_profit_multiplier = take_profit_multiplier
        self.volatility_factor = volatility_factor
        self.last_trade = None

        print(f"Symbol: {self.symbol}")
        print(f"Moving Average Period: {self.moving_average_period}")
        print(f"Cash at Risk: {self.cash_at_risk}")
        print(f"Volatility Period: {self.volatility_period}")
        print(f"Stop Loss Multiplier: {self.stop_loss_multiplier}")
        print(f"Take Profit Multiplier: {self.take_profit_multiplier}")

    def on_trading_iteration(self):
        cash, last_price, quantity, volatility = self._position_sizing()
        moving_average = self._get_moving_average()

        if cash <= last_price:
            return

        if self._should_buy(last_price, moving_average):
            self._execute_buy_order(quantity, last_price, volatility)
        elif self._should_sell(last_price, moving_average):
            self._execute_sell_order(quantity, last_price, volatility)

    def _position_sizing(self) -> Tuple[float, float, int, float]:
        """Calculate position size based on available cash, risk, and volatility."""
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        volatility = self._get_volatility()

        adjusted_cash_at_risk = self.cash_at_risk / (1 + volatility)
        quantity = round(cash * adjusted_cash_at_risk / last_price, 0)

        return cash, last_price, quantity, volatility

    def _get_volatility(self) -> float:
        """Calculate volatility of the asset over a specific period."""
        bars = self.get_historical_prices(self.symbol, self.volatility_period, "day")
        closing_prices = bars.df["close"]
        returns = np.diff(np.log(closing_prices))
        return np.std(returns)

    def _get_moving_average(self) -> float:
        """Calculate the moving average of the price over the defined period."""
        bars = self.get_historical_prices(
            self.symbol, self.moving_average_period, "day"
        )
        closing_prices = bars.df["close"]
        return np.mean(closing_prices)

    def _should_buy(self, last_price: float, moving_average: float) -> bool:
        """Buy if the price is above the moving average (upward trend)."""
        return last_price > moving_average

    def _should_sell(self, last_price: float, moving_average: float) -> bool:
        """Sell if the price is below the moving average (downward trend)."""
        return last_price < moving_average

    def _execute_buy_order(self, quantity: int, last_price: float, volatility: float):
        """Execute a buy order with stop-loss and take-profit based on volatility."""
        if self.last_trade == "sell":
            self.sell_all()

        stop_loss_price = last_price * (
            self.stop_loss_multiplier - volatility * self.volatility_factor
        )
        take_profit_price = last_price * (
            self.take_profit_multiplier + volatility * self.volatility_factor
        )

        order = self.create_order(
            self.symbol,
            quantity,
            "buy",
            type="bracket",
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
        )
        self.submit_order(order)
        self.last_trade = "buy"

    def _execute_sell_order(self, quantity: int, last_price: float, volatility: float):
        """Execute a sell order with stop-loss and take-profit based on volatility."""
        if self.last_trade == "buy":
            self.sell_all()

        stop_loss_price = last_price * (
            self.stop_loss_multiplier + volatility * self.volatility_factor
        )
        take_profit_price = last_price * (
            self.take_profit_multiplier - volatility * self.volatility_factor
        )

        order = self.create_order(
            self.symbol,
            quantity,
            "sell",
            type="bracket",
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
        )
        self.submit_order(order)
        self.last_trade = "sell"
