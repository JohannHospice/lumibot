from lumibot.strategies import Strategy


class MarketMakingStrategy(Strategy):
    parameters = {
        "symbol": "MSFT",
        "spread_percentage": 0.002,
        "order_size_percentage": 0.05,
        "update_interval": "1m",
    }

    def initialize(self):
        self.sleeptime = self.parameters["update_interval"]
        self.symbol = self.parameters["symbol"]
        self.spread_percentage = self.parameters["spread_percentage"]
        self.order_size_percentage = self.parameters["order_size_percentage"]

    def on_trading_iteration(self):
        self.sell_all(True)

        quantity, buy_price, sell_price = self._get_order_quantity_and_prices()

        self.submit_orders(
            [
                self.create_order(
                    self.symbol, quantity=quantity, side="buy", limit_price=buy_price
                ),
                self.create_order(
                    self.symbol, quantity=quantity, side="sell", limit_price=sell_price
                ),
            ]
        )

    def _get_order_quantity_and_prices(self):
        last_price = self.get_last_price(self.symbol)

        buy_price = last_price * (1 - self.spread_percentage / 2)
        sell_price = last_price * (1 + self.spread_percentage / 2)
        quantity = (self.cash * self.order_size_percentage) / last_price

        return quantity, buy_price, sell_price
