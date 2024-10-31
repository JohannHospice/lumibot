from lumibot.strategies import Strategy


class MarketMakingStrategy(Strategy):
    parameters = {
        "symbol": "BTC/USD",
        "spread_percentage": 0.002,
        "order_size_percentage": 0.05,
        "update_interval": "1m",
    }

    def initialize(self, symbol=None):
        self.sleeptime = self.parameters["update_interval"]
        self.symbol = symbol if symbol else self.parameters["symbol"]
        self.spread_percentage = self.parameters["spread_percentage"]
        self.order_size_percentage = self.parameters["order_size_percentage"]
        print(f"Initialized Market Making Strategy for {self.symbol}")

    def on_trading_iteration(self):
        self.sell_all(True)

        quantity, buy_price, sell_price = self._get_order_quantity_and_prices()

        buy_order = self.create_order(
            self.symbol,
            quantity=quantity,
            side="buy",
            limit_price=buy_price,
            time_in_force="day",
        )

        sell_order = self.create_order(
            self.symbol,
            quantity=quantity,
            side="sell",
            limit_price=sell_price,
            time_in_force="day",
        )
        self.submit_orders([buy_order, sell_order])

    def _get_order_quantity_and_prices(self):
        last_price = self.get_last_price(self.symbol)

        buy_price = round(last_price * (1 - self.spread_percentage / 2), 2)
        sell_price = round(last_price * (1 + self.spread_percentage / 2), 2)
        quantity = round((self.cash * self.order_size_percentage) / last_price)

        return quantity, buy_price, sell_price
