from typing import Tuple, List
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

device = "cuda:0" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(
    device
)
labels = ["positive", "negative", "neutral"]


def estimate_sentiment(news: List[str]) -> Tuple[float, str]:
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
