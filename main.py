import requests
from dotenv import load_dotenv
from datetime import datetime
import csv
import os


load_dotenv()
api_key = os.getenv("API_KEY")
TROY_OUNCE_GRAMS = 31.1035

url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=INR&currencies=XAU,XAG"

response = requests.get(url)
data = response.json()
rates = data['rates']

dt_object = datetime.fromtimestamp(data['timestamp'])
date = dt_object.strftime("%Y-%m-%d")
time = dt_object.strftime("%H:%M")

gold_price = rates['INRXAU']
silver_price = rates['INRXAG']

gold_price_24k_per_gram = gold_price / TROY_OUNCE_GRAMS
gold_price_22k_per_gram = gold_price_24k_per_gram * 0.916
gold_price_18k_per_gram = gold_price_24k_per_gram * 0.750

silver_price_per_gram = silver_price / TROY_OUNCE_GRAMS
silver_price_per_kg = silver_price_per_gram * 1000

file_exists = os.path.exists("rates.csv")
with open("rates.csv", "a", newline="") as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(["date", "time", "gold_price_24k", "gold_price_22k", "gold_price_18k",
                         "silver_price_g", "silver_price_kg"])
    writer.writerow([date, time, f"{gold_price_24k_per_gram:.2f}", f"{gold_price_22k_per_gram:.2f}",
                     f"{gold_price_18k_per_gram:.2f}", f"{silver_price_per_gram:.2f}", f"{silver_price_per_kg:.2f}"])

print("Data saved successfully!")
