from get_sentiment_and_news import GetSentimentAndNews
from alpaca_trade_api import REST
import gc
import os
from typing import List, Tuple

FORCE_NO_CACHE = False


class GetSentimentAndNewsCached(GetSentimentAndNews):
    def __init__(self, symbol: str, limit: int, get_news: REST.get_news):
        super().__init__(symbol, limit, get_news)

    def get_news_and_sentiment(
        self, dates: Tuple[str, str]
    ) -> Tuple[List[str], float, str, int]:
        to_date, from_date = dates
        cache_file = self._get_cache_file_path(to_date, from_date)

        if not FORCE_NO_CACHE and os.path.exists(cache_file):
            return self._read_cached_news_and_sentiment(cache_file)

        news_headlines, probability, sentiment, num_headlines = (
            super().get_news_and_sentiment((to_date, from_date))
        )

        self._write_cache_news_and_sentiment(
            cache_file, probability, sentiment, news_headlines
        )

        gc.collect()

        return news_headlines, probability, sentiment, num_headlines

    def _get_cache_file_path(self, to_date, from_date):
        return f"./cache/news/{self.symbol}/sentiment_{self.symbol}_{from_date}-{to_date}_{self.limit}.txt"

    def _read_cached_news_and_sentiment(self, cache_file):
        with open(cache_file, "r") as f:
            lines = f.readlines()
            probability = float(lines[0].strip())
            sentiment = lines[1].strip()
            headlines = [line.strip() for line in lines[2:]]
        return headlines, probability, sentiment, len(headlines)

    def _write_cache_news_and_sentiment(
        self, cache_file, probability, sentiment, news_headlines
    ):
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)

        with open(cache_file, "w") as f:
            f.write(f"{probability}\n")
            f.write(f"{sentiment}\n")
            for headline in news_headlines:
                f.write(headline + "\n")

        gc.collect()
