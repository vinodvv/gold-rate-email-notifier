import requests
from dotenv import load_dotenv
from datetime import datetime
import csv
import os

# Constants
CSV_FILE = "rates.csv"
TROY_OZ_GRAMS = 31.1035
GOLD_RATIOS = {"24k": 1.0, "22k": 0.916, "18k": 0.750}


def load_credentials():
    """Load API key from .env file."""
    load_dotenv(override=True)
    api_key = os.getenv("API_KEY")
    if api_key is None:
        raise ValueError("API_KEY not found in .env file")
    return api_key


def get_gold_silver_rate(api_key):
    """
    Fetch gold/silver rates from MetalPriceAPI.
    :param api_key:
    :return: rates, formatted_date, formatted_time
    """
    url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=INR&currencies=XAU,XAG"

    response = requests.get(url)
    data = response.json()
    if not data.get("success"):
        raise ValueError(f"API error: {data.get('error', 'Unknown error')}")
    if 'rates' not in data or 'timestamp' not in data:
        raise KeyError("Missing expected keys in API response.")
    rates = data['rates']
    dt_object = datetime.fromtimestamp(data['timestamp'])
    formatted_date = dt_object.strftime("%Y-%m-%d")
    formatted_time = dt_object.strftime("%H:%M")
    return rates, formatted_date, formatted_time


def compute_prices(gold_price, silver_price):
    """Compute gold and silver prices per gram, per, karat, and per kg."""
    gold_24k_per_gram = gold_price / TROY_OZ_GRAMS
    prices = {
        "gold_24k_per_gram": gold_24k_per_gram,
        "gold_22k_per_gram": gold_24k_per_gram * GOLD_RATIOS["22k"],
        "gold_18k_per_gram": gold_24k_per_gram * GOLD_RATIOS["18k"],
        "silver_per_gram": silver_price / TROY_OZ_GRAMS,
    }
    prices["silver_per_kg"] = prices["silver_per_gram"] * 1000
    return prices


def save_gold_silver_rates(filepath, date, time, prices):
    """Append rates to CSV, writing header if file doesn't exits."""
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "date", "time",
                "gold_price_24k", "gold_price_22k", "gold_price_18k",
                "silver_price_g", "silver_price_kg"
            ])
        writer.writerow([
            date, time,
            f"{prices['gold_24k_per_gram']:.2f}",
            f"{prices['gold_22k_per_gram']:.2f}",
            f"{prices['gold_18k_per_gram']:.2f}",
            f"{prices['silver_per_gram']:.2f}",
            f"{prices['silver_per_kg']:.2f}",
        ])


def main():
    api_key = load_credentials()
    rates, date, time = get_gold_silver_rate(api_key)

    gold_price = rates['INRXAU']
    silver_price = rates['INRXAG']

    prices = compute_prices(gold_price, silver_price)
    save_gold_silver_rates(CSV_FILE, date, time, prices)
    print(f"Gold, Silver rates as on {date} saved successfully!")


if __name__ == "__main__":
    main()
