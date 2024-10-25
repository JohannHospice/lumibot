from lumibot.entities import TradingFee
from sentiment_strategy import SentimentStrategy
from momentum_strategy import MomentumStrategy

STRATEGIES = {
    "sentiment": SentimentStrategy,
    "momentum": MomentumStrategy,
}

BROKER_FEES = {
    "Interactive Brokers": {
        "buy_trading_fees": [
            TradingFee(flat_fee=0),  # IBKR Lite (sans frais)
            TradingFee(percent_fee=0.0005),  # IBKR Pro, frais variables par action
        ],
        "sell_trading_fees": [
            TradingFee(flat_fee=0),
            TradingFee(percent_fee=0.0005),  # Même que pour l'achat
        ],
    },
    "Alpaca": {
        "buy_trading_fees": [
            TradingFee(flat_fee=0),  # Aucun frais
            TradingFee(percent_fee=0),
        ],
        "sell_trading_fees": [TradingFee(flat_fee=0), TradingFee(percent_fee=0)],
    },
    "Binance": {
        "buy_trading_fees": [
            TradingFee(flat_fee=0),
            TradingFee(percent_fee=0.10),  # 0,10 % par transaction
        ],
        "sell_trading_fees": [
            TradingFee(flat_fee=0),
            TradingFee(percent_fee=0.10),  # Même pour la vente
        ],
    },
    "TD Ameritrade": {
        "buy_trading_fees": [
            TradingFee(flat_fee=0),  # Aucun frais
            TradingFee(percent_fee=0),
        ],
        "sell_trading_fees": [TradingFee(flat_fee=0), TradingFee(percent_fee=0)],
    },
    "Kraken": {
        "buy_trading_fees": [
            TradingFee(flat_fee=0),
            TradingFee(percent_fee=0.16),  # 0,16 % pour les "makers"
        ],
        "sell_trading_fees": [
            TradingFee(flat_fee=0),
            TradingFee(percent_fee=0.26),  # 0,26 % pour les "takers"
        ],
    },
}
