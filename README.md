# lumibot

lumibot is a trading bot that allows you to run and backtest trading strategies using various data sources and brokers.

## Prerequisites
- Python 3.8 or higher
- Pipenv
- [Alpaca API key and secret (only for live trading)](https://alpaca.markets/)

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/johannhospice/lumibot.git
    cd lumibot
    ```

2. **Create and activate a virtual environment**:
    ```sh
    chmod +x install.sh
    ./install.sh
    ```

3. **Set up environment variables**:
    - Create a `.env` file in the root directory of the project.
    - Add your API credentials and other necessary environment variables to the `.env` file. For example:
        ```sh
        API_KEY=your_alpaca_api_key
        API_SECRET=your_alpaca_secret_key
        BASE_URL=https://paper-api.alpaca.markets
        PAPER=True
        ```

## Usage

### Help documentation

To view the help documentation, use the following command:
```sh
./app --help
```
or
```sh
./app <command> --help
```

### Backtesting a Strategy

To backtest a strategy, use the following command:
```sh
./app backtest SPY -d 3 -nl 10 -sd 2022-01-01 -ed 2024-10-1
```

- SPY: The symbol of the asset to backtest.
- -d 3: The duration of the backtest in days.
- -nl 10: The number of news headlines to consider.
- -sd 2022-01-01: The start date for the backtest.
- -ed 2024-10-1: The end date for the backtest.

### Running a Strategy

To run a strategy, use the following command:
```sh
./app run SPY -nl 10
```

### Listing Available Assets

To list all available assets of a given class from the broker, use the following command:
```sh
./app list -c <asset_class>
```
- <asset_class>: The class of assets to list (e.g., us_equity, crypto).

## Credits

This work is inspired from [MLTradingBot](https://github.com/nicknochnack/MLTradingBot)