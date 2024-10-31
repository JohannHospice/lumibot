from strategies.sentiment_strategy import SentimentStrategy
from strategies.momentum_strategy import MomentumStrategy
from strategies.market_making_strategy import MarketMakingStrategy
from strategies.fourier_transform_strategy import FourierTransformStrategy
from strategies.improved_market_making_strategy import ImprovedMarketMakingStrategy
from strategies.price_action_strategy import PriceActionStrategy

STRATEGIES = {
    "sentiment": SentimentStrategy,
    "momentum": MomentumStrategy,
    "fourier_transform": FourierTransformStrategy,
    "market_making": MarketMakingStrategy,
    "improved_market_making_strategy": ImprovedMarketMakingStrategy,
    "price_action": PriceActionStrategy,
}
