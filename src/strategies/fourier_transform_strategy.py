from lumibot.strategies.strategy import Strategy
import numpy as np
import pandas as pd
import scipy.fftpack as fft


class FourierTransformStrategy(Strategy):
    # Configuration de la stratégie
    parameters = {
        "symbols": ["SPY", "AAPL", "DIA"],
        "order_size": 0.01,  # Taille de chaque ordre
        "window_size": 100,  # Taille de la fenêtre pour la transformée de Fourier
        "stop_loss_pct": 0.02,  # Stop-loss à 2%
        "take_profit_pct": 0.04,  # Prise de profit à 4%
        "long_short": "both",  # Options: "long", "short", "both"
    }

    def initialize(self):
        self.active_orders = {}
        self.sleeptime = "1m"

    def on_trading_iteration(self):
        # for symbol in self.parameters["symbols"]:
        symbol = "SPY"
        # Obtenir les données historiques
        closes = self.get_historical_prices(symbol, 1, "minute").df["close"]

        if len(closes) < self.parameters["window_size"]:
            pass
            # continue  # Attendre d'avoir suffisamment de données

        # Ajouter les nouvelles données au DataFrame

        signal = self.apply_fourier_transform(closes)

        # Générer des signaux d'achat/vente
        signal_value = signal.iloc[-1]
        if signal_value > 0:
            # Signal d'achat
            if self.parameters["long_short"] in ["long", "both"]:
                self.open_position(symbol, "long")
        elif signal_value < 0:
            # Signal de vente
            if self.parameters["long_short"] in ["short", "both"]:
                self.open_position(symbol, "short")

    def apply_fourier_transform(self, price_series):
        print(price_series)
        # Calculer la transformée de Fourier
        fft_result = fft.fft(price_series)
        # Filtrer les fréquences (par exemple, garder les basses fréquences)
        fft_filtered = np.zeros_like(fft_result)
        fft_filtered[:5] = fft_result[:5]  # Garder les 5 premières composantes
        # Revenir dans le domaine temporel
        filtered_signal = fft.ifft(fft_filtered)
        # Retourner le signal filtré
        return pd.Series(np.real(filtered_signal), index=price_series.index)

    def open_position(self, coin, position_type):
        # Vérifier si une position est déjà ouverte pour ce coin et ce type
        position_key = f"{coin}_{position_type}"
        if position_key in self.active_orders:
            return  # Ne pas ouvrir une autre position du même type

        # Déterminer la quantité à acheter/vendre
        quantity = self.parameters["order_size"]

        if position_type == "long":
            # Passer un ordre d'achat
            order = self.create_order(
                symbol=coin,
                quantity=quantity,
                side="buy",
                order_type="market",
            )
        elif position_type == "short":
            # Passer un ordre de vente (vente à découvert)
            order = self.create_order(
                symbol=coin,
                quantity=quantity,
                side="sell",
                order_type="market",
            )

        # Enregistrer l'ordre actif
        self.active_orders[position_key] = {
            "order": order,
            "entry_price": self.get_last_price(coin),
            "position_type": position_type,
        }

    def on_order_filled(self, order):
        # Une fois l'ordre exécuté, définir les stop-loss et take-profit
        position_key = f"{order.symbol}_{order.side.lower()}"
        if position_key in self.active_orders:
            entry_price = self.active_orders[position_key]["entry_price"]
            stop_loss_price = entry_price * (
                1 - self.parameters["stop_loss_pct"]
                if order.side.lower() == "buy"
                else 1 + self.parameters["stop_loss_pct"]
            )
            take_profit_price = entry_price * (
                1 + self.parameters["take_profit_pct"]
                if order.side.lower() == "buy"
                else 1 - self.parameters["take_profit_pct"]
            )

            # Définir le stop-loss
            self.create_order(
                symbol=order.symbol,
                quantity=order.quantity,
                side="sell" if order.side.lower() == "buy" else "buy",
                order_type="stop",
                stop_price=stop_loss_price,
            )

            # Définir la prise de profit
            self.create_order(
                symbol=order.symbol,
                quantity=order.quantity,
                side="sell" if order.side.lower() == "buy" else "buy",
                order_type="limit",
                limit_price=take_profit_price,
            )

    def on_order_closed(self, order):
        # Supprimer la position active
        position_key = f"{order.symbol}_{order.side.lower()}"
        if position_key in self.active_orders:
            del self.active_orders[position_key]

    def on_strategy_end(self):
        # Clôturer toutes les positions à la fin de la stratégie
        for position_key, info in self.active_orders.items():
            order = info["order"]
            # Passer un ordre de clôture
            self.create_order(
                symbol=order.symbol,
                quantity=order.quantity,
                side="sell" if order.side.lower() == "buy" else "buy",
                order_type="market",
            )
