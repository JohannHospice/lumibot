from dotenv import load_dotenv
import os


def load_api_credentials():
    load_dotenv()

    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    PAPER = os.getenv("PAPER", "True").lower() in ["true", "1", "t"]
    BASE_URL = os.getenv("BASE_URL")

    if not API_KEY or not API_SECRET:
        raise ValueError("API_KEY and API_SECRET must be set in the .env file")

    return {API_KEY, API_SECRET, PAPER, BASE_URL}
