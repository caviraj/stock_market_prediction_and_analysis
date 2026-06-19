import argparse
from rf_classifier import train_rf

def main():
    parser = argparse.ArgumentParser(description='Train Random Forest classifier for stock signals')
    parser.add_argument('--ticker', type=str, required=True, help='Stock ticker (e.g. TCS)')
    args = parser.parse_args()
    ticker = args.ticker

    train_rf(ticker)

if __name__ == "__main__":
    main()
