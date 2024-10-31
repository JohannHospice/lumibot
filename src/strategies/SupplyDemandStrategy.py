from lumibot.strategies import Strategy
import pandas as pd


class SupplyDemandStrategy(Strategy):
    parameters = {
        "symbol": "BTC/USD",
        "demand_threshold": 5,  # Nombre de bougies de rebond pour créer une zone de demande
        "supply_threshold": 5,  # Nombre de bougies de baisse pour créer une zone d'offre
        "stop_loss_percentage": 0.02,  # Stop loss à 2% en dessous du niveau de demande / au-dessus du niveau d’offre
        "take_profit_percentage": 0.05,  # Take profit à 5% au-dessus du niveau de demande / en dessous du niveau d’offre
        "order_size_percentage": 0.05,  # Taille de chaque ordre en pourcentage du portefeuille
    }

    def initialize(self, symbol=None):
        self.symbol = symbol if symbol else self.parameters["symbol"]
        self.demand_zones = []
        self.supply_zones = []
        print(f"Initialized Supply and Demand Strategy for {self.symbol}")

    def on_trading_iteration(self):
        # Charger les données de prix
        historical_data = self.get_historical_data(
            self.symbol, "1h", 100
        )  # 100 dernières bougies en 1 heure
        if historical_data is None or len(historical_data) < 10:
            print("Pas assez de données pour analyser les zones de supply et demand.")
            return

        # Détecter les zones de demande et d'offre
        self.detect_demand_zones(historical_data)
        self.detect_supply_zones(historical_data)

        # Vérifier si le prix actuel est dans une zone de demande
        current_price = self.get_last_price(self.symbol)
        demand_zone = self.is_in_demand_zone(current_price)
        supply_zone = self.is_in_supply_zone(current_price)

        # Prendre position si le prix est dans une zone de demande ou d'offre
        if demand_zone:
            self.place_order("buy", demand_zone, current_price)
        elif supply_zone:
            self.place_order("sell", supply_zone, current_price)

    def detect_demand_zones(self, data):
        # Détecte les zones où le prix rebondit, créant une zone de demande
        for i in range(
            self.parameters["demand_threshold"],
            len(data) - self.parameters["demand_threshold"],
        ):
            low = data["low"][i]
            # Vérifier si le prix rebondit après avoir atteint ce niveau
            if all(
                data["low"][i] < data["low"][i - j]
                for j in range(1, self.parameters["demand_threshold"])
            ):
                self.demand_zones.append(low)

    def detect_supply_zones(self, data):
        # Détecte les zones où le prix baisse après avoir atteint un certain niveau, créant une zone d'offre
        for i in range(
            self.parameters["supply_threshold"],
            len(data) - self.parameters["supply_threshold"],
        ):
            high = data["high"][i]
            # Vérifier si le prix baisse après avoir atteint ce niveau
            if all(
                data["high"][i] > data["high"][i + j]
                for j in range(1, self.parameters["supply_threshold"])
            ):
                self.supply_zones.append(high)

    def is_in_demand_zone(self, price):
        # Vérifie si le prix actuel est dans une zone de demande
        return any(
            abs(zone - price) / zone < 0.01 for zone in self.demand_zones
        )  # marge de 1%

    def is_in_supply_zone(self, price):
        # Vérifie si le prix actuel est dans une zone d'offre
        return any(
            abs(zone - price) / zone < 0.01 for zone in self.supply_zones
        )  # marge de 1%

    def place_order(self, side, zone, price):
        # Calcul du stop loss et du take profit
        if side == "buy":
            stop_loss = price * (1 - self.parameters["stop_loss_percentage"])
            take_profit = price * (1 + self.parameters["take_profit_percentage"])
        else:
            stop_loss = price * (1 + self.parameters["stop_loss_percentage"])
            take_profit = price * (1 - self.parameters["take_profit_percentage"])

        # Taille de la position
        quantity = round(
            (self.cash * self.parameters["order_size_percentage"]) / price, 2
        )

        # Création de l'ordre
        order = self.create_order(
            self.symbol,
            quantity=quantity,
            side=side,
            stop_loss_price=stop_loss,
            take_profit_price=take_profit,
            time_in_force="day",
        )
        self.submit_order(order)
        print(
            f"Placed {side} order at {price} with stop loss at {stop_loss} and take profit at {take_profit}"
        )
