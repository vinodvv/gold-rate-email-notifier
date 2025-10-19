import requests
from dotenv import load_dotenv
from datetime import datetime
import csv
import os


def load_credentials():
    load_dotenv(override=True)
    api_key = os.getenv("API_KEY")
    if api_key is None:
        raise ValueError("API_KEY not found in .env file")
    print("Fetched API_KEY: ", api_key)
    troy_oz_grams = 31.1035
    return api_key, troy_oz_grams


def get_gold_silver_rate(api_key):
    url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=INR&currencies=XAU,XAG"

    response = requests.get(url)
    data = response.json()
    rates = data['rates']
    dt_object = datetime.fromtimestamp(data['timestamp'])
    formatted_date = dt_object.strftime("%Y-%m-%d")
    formatted_time = dt_object.strftime("%H:%M")
    return rates, formatted_date, formatted_time


def save_gold_silver_rates(filepath, date, time, gold_price_24k, gold_price_22k,
                           gold_price_18k, silver_price_g, silver_price_kg):
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["date", "time", "gold_price_24k", "gold_price_22k", "gold_price_18k",
                             "silver_price_g", "silver_price_kg"])
        writer.writerow([date, time, f"{gold_price_24k_per_gram:.2f}", f"{gold_price_22k_per_gram:.2f}",
                         f"{gold_price_18k_per_gram:.2f}", f"{silver_price_per_gram:.2f}",
                         f"{silver_price_per_kg:.2f}"])


api_key, troy_oz_grams = load_credentials()
rates, date, time = get_gold_silver_rate(api_key)
filename = "rates.csv"

gold_price = rates['INRXAU']
silver_price = rates['INRXAG']

gold_price_24k_per_gram = gold_price / troy_oz_grams
gold_price_22k_per_gram = gold_price_24k_per_gram * 0.916
gold_price_18k_per_gram = gold_price_24k_per_gram * 0.750

silver_price_per_gram = silver_price / troy_oz_grams
silver_price_per_kg = silver_price_per_gram * 1000

save_gold_silver_rates(filename, date, time, gold_price_24k_per_gram, gold_price_22k_per_gram,
                       gold_price_18k_per_gram, silver_price_per_gram, silver_price_per_kg)

print("Data saved successfully!")
