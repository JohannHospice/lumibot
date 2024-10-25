from argument_parser import parse_arguments
from commands import backtest_strategy, list_assets, run_strategy
from credentials import load_api_credentials
from utils import build_parameters, create_broker, create_strategy, create_trading_fees


def main():
    API_KEY, API_SECRET, PAPER, BASE_URL = load_api_credentials()
    parser, args = parse_arguments()

    broker = create_broker(API_KEY, API_SECRET, PAPER)

    if args.mode == "list":
        list_assets(broker, args.asset_class)
        return

    parameters = build_parameters(args, API_KEY, API_SECRET, BASE_URL)

    strategy = create_strategy(args.strategy, broker, parameters)

    if args.mode == "run":
        run_strategy(strategy)
    elif args.mode == "backtest":
        trading_fees = create_trading_fees(args)
        backtest_strategy(
            strategy=strategy,
            start_date=args.start_date,
            end_date=args.end_date,
            parameters=parameters,
            trading_fees=trading_fees,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
