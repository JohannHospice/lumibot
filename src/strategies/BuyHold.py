from lumibot.strategies import Strategy


class BuyHold(Strategy):

    def initialize(self):
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        if self.first_iteration:
            symbol = "GOOG"
            price = self.get_last_price(symbol)
            quantity = self.cash // price
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)
