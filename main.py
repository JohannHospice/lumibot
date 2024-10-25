from argument_parser import parse_arguments
from credentials import load_api_credentials
from constants import COMMANDS


def main():
    credentials = load_api_credentials()
    parser, args = parse_arguments()

    if args.mode in COMMANDS:
        command = COMMANDS[args.mode]
        command(args, credentials)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
