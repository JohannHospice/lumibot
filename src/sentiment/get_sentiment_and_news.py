from estimate_sentiment import estimate_sentiment
from alpaca_trade_api import REST
from typing import List, Tuple


class GetSentimentAndNews:
    def __init__(self, symbol: str, limit: int, get_news: REST.get_news):
        self.symbol = symbol
        self.get_news = get_news
        self.limit = limit

    def get_news_and_sentiment(
        self, dates: Tuple[str, str]
    ) -> Tuple[List[str], float, str, int]:
        news_headlines = self._fetch_news_headlines(dates)

        probability, sentiment = estimate_sentiment(news_headlines)

        return news_headlines, probability, sentiment, len(news_headlines)

    def _fetch_news_headlines(self, dates: Tuple[str, str]) -> List[str]:
        to_date, from_date = dates
        news = self.get_news(
            symbol=self.symbol, start=from_date, end=to_date, limit=self.limit
        )
        return [ev.__dict__["_raw"]["headline"] for ev in news]
