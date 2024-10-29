from lumibot.strategies import Strategy
import pandas as pd


class ImprovedMarketMakingStrategy(Strategy):
    parameters = {
        "symbol": "AAPL",
        "base_spread_percentage": 0.001,  # Spread de base réduit
        "order_size_percentage": 0.5,  # Taille de l'ordre ajustée
        "volatility_period": 20,  # Période pour le calcul de l'ATR
        "update_interval": "5m",  # Intervalle de mise à jour ajusté
        "max_order_size_percentage": 0.2,  # Taille maximale de l'ordre
        "min_order_size_percentage": 0.05,  # Taille minimale de l'ordre
        "atr_multiplier": 1.5,  # Multiplicateur pour le spread dynamique
        "stop_loss_percentage": 0.02,  # Par exemple, 2%
    }

    def initialize(self):
        self.sleeptime = self.parameters["update_interval"]
        self.symbol = self.parameters["symbol"]
        self.base_spread_percentage = self.parameters["base_spread_percentage"]
        self.order_size_percentage = self.parameters["order_size_percentage"]
        self.volatility_period = self.parameters["volatility_period"]
        self.max_order_size_percentage = self.parameters["max_order_size_percentage"]
        self.min_order_size_percentage = self.parameters["min_order_size_percentage"]
        self.atr_multiplier = self.parameters["atr_multiplier"]
        self.stop_loss_percentage = self.parameters["stop_loss_percentage"]

    def on_trading_iteration(self):

        # Éviter de trader pendant l'ouverture et la fermeture du marché
        current_time = self.get_datetime("US/Eastern").time()
        if (
            current_time < pd.Timestamp("09:45").time()
            or current_time > pd.Timestamp("15:45").time()
        ):
            return

        if self.get_cash() < 1:
            print("Pas assez de cash")
            return

        self.cancel_open_orders()

        quantity, buy_price, sell_price = self._get_order_quantity_and_prices()

        self.submit_order(
            self.create_order(
                self.symbol,
                quantity=quantity,
                side="buy",
                limit_price=buy_price,
                stop_loss_price=buy_price * (1 - self.stop_loss_percentage),
            )
        )
        self.submit_order(
            self.create_order(
                self.symbol,
                quantity=quantity,
                side="sell",
                limit_price=sell_price,
                stop_loss_price=sell_price * (1 + self.stop_loss_percentage),
            )
        )

        print(f"Ordres placés - Achat: {buy_price}, Vente: {sell_price}")

    def _get_order_quantity_and_prices(
        self,
    ):
        # Calcul de l'ATR pour ajuster le spread dynamiquement
        historical_data = self.get_historical_prices(
            self.symbol,
            length=self.volatility_period
            + 1,  # +1 pour compenser le décalage du calcul
            timestep="day",
        ).df

        atr = self.calculate_atr(historical_data, self.volatility_period)
        last_price = self.get_last_price(self.symbol)
        cash = self.get_cash()

        atr_percentage = atr / last_price

        # Ajustement du spread en fonction de la volatilité
        spread_percentage = max(
            self.base_spread_percentage, atr_percentage * self.atr_multiplier
        )

        # Ajustement de la taille de l'ordre en fonction de la volatilité
        order_size_percentage = max(
            self.min_order_size_percentage,
            min(
                self.order_size_percentage
                / (atr_percentage if atr_percentage != 0 else 1),
                self.max_order_size_percentage,
            ),
        )

        buy_price = last_price * (1 - spread_percentage / 2)
        sell_price = last_price * (1 + spread_percentage / 2)

        quantity = (cash * order_size_percentage) / last_price

        return quantity, buy_price, sell_price

    def calculate_atr(self, data, period):
        # Préparation des données pour le calcul de l'ATR
        data = data.copy()
        data["prior_close"] = data["close"].shift(1)
        data["high_low"] = data["high"] - data["low"]
        data["high_close"] = abs(data["high"] - data["prior_close"])
        data["low_close"] = abs(data["low"] - data["prior_close"])
        tr = data[["high_low", "high_close", "low_close"]].max(axis=1)

        return tr.rolling(window=period).mean().iloc[-1]

    def is_market_trending(self):
        historical_data = self.get_historical_prices(
            self.symbol,
            length=50,  # Période pour la moyenne mobile
            timestep="day",
        ).df
        sma_short = historical_data["close"].rolling(window=20).mean().iloc[-1]
        sma_long = historical_data["close"].rolling(window=50).mean().iloc[-1]
        return sma_short > sma_long  # Tendance haussière
