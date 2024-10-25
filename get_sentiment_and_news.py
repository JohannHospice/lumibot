from typing import Tuple, List
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from alpaca_trade_api import REST
import torch
import os
import gc

device = "cuda:0" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(
    device
)
labels = ["positive", "negative", "neutral"]
NO_CACHE = False


class GetSentimentAndNews:
    def __init__(self, symbol: str, limit: int, get_news: REST.get_news):
        self.symbol = symbol
        self.get_news = get_news
        self.limit = limit

    def get_news_and_sentiment(
        self, dates: Tuple[str, str]
    ) -> Tuple[List[str], float, str, int]:
        news_headlines = self._fetch_news_headlines(dates)

        probability, sentiment = self._estimate_sentiment(news_headlines)

        return news_headlines, probability, sentiment, len(news_headlines)

    def _fetch_news_headlines(self, dates: Tuple[str, str]) -> List[str]:
        to_date, from_date = dates
        news = self.get_news(
            symbol=self.symbol, start=from_date, end=to_date, limit=self.limit
        )
        return [ev.__dict__["_raw"]["headline"] for ev in news]

    def _estimate_sentiment(self, news: List[str]) -> Tuple[float, str]:
        if not news:
            return 0, labels[-1]

        tokens = tokenizer(news, return_tensors="pt", padding=True).to(device)

        result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])[
            "logits"
        ]
        result = torch.nn.functional.softmax(torch.sum(result, 0), dim=-1)
        probability = result[torch.argmax(result)]
        sentiment = labels[torch.argmax(result)]
        return probability, sentiment


class GetSentimentAndNewsCached(GetSentimentAndNews):
    def __init__(self, symbol: str, limit: int, get_news: REST.get_news):
        super().__init__(symbol, limit, get_news)

    def get_news_and_sentiment(
        self, dates: Tuple[str, str]
    ) -> Tuple[List[str], float, str, int]:
        to_date, from_date = dates
        cache_file = self._get_cache_file_path(to_date, from_date)

        if not NO_CACHE and os.path.exists(cache_file):
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
