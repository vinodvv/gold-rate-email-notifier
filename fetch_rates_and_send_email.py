import requests
from dotenv import load_dotenv
from datetime import datetime
import csv
import os
import smtplib
from email.message import EmailMessage


# Constants
CSV_FILE = "rates.csv"
TROY_OZ_GRAMS = 31.1035
GOLD_RATIOS = {"24k": 1.0, "22k": 0.916, "18k": 0.750}
INR_SYMBOL = "\u20B9"


def load_credentials():
    """Load API key, email credentials  from a .env file."""
    load_dotenv(override=True)
    api_key = os.getenv("API_KEY")
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    missing = []
    if not api_key: missing.append("API_KEY")
    if not email_address: missing.append("EMAIL_ADDRESS")
    if not email_password: missing.append("EMAIL_PASSWORD")
    if missing:
        raise ValueError("Missing variables in .env file: " + ", ".join(missing))
    return api_key, email_address, email_password


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
    prices["gold_24k_8gram"] = prices["gold_24k_per_gram"] * 8
    prices["gold_24k_10gram"] = prices["gold_24k_per_gram"] * 10
    prices["gold_22k_8gram"] = prices["gold_22k_per_gram"] * 8
    prices["gold_22k_10gram"] = prices["gold_22k_per_gram"] * 10
    prices["gold_18k_8gram"] = prices["gold_18k_per_gram"] * 8
    prices["gold_18k_10gram"] = prices["gold_18k_per_gram"] * 10
    prices["silver_per_kg"] = prices["silver_per_gram"] * 1000
    return prices


def save_gold_silver_rates(filepath, date, time, prices):
    """Append rates to CSV, writing header if file doesn't exist."""
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


def login_to_email(email_address, email_password):
    """Log in to the Gmail SMTP server"""
    try:
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login(email_address, email_password)
        return smtp
    except Exception as e:
        raise ConnectionError("SMTP login failed: " + str(e))


def create_email(prices, sender_name, recipient, recipient_name):
    """Create an email"""
    msg = EmailMessage()
    msg["Subject"] = f"🪙 Today's Gold, Silver Prices"
    msg["From"] = sender_name
    msg["To"] = recipient

    # Plain text
    text_content = (
        f"Hi {recipient_name},\n\n"
        f"Today's Gold, Silver Prices:\n\n"
        f"1. GOLD\n"
        f"  (a) 24k: {INR_SYMBOL} {prices['gold_24k_per_gram']:.2f} per gram | "
        f"{INR_SYMBOL} {prices['gold_24k_8gram']:.2f} (8g) | "
        f"{INR_SYMBOL} {prices['gold_24k_10gram']:.2f} (10g)\n"
        f"  (b) 22k: {INR_SYMBOL} {prices['gold_22k_per_gram']:.2f} per gram | "
        f"{INR_SYMBOL} {prices['gold_22k_8gram']:.2f} (8g) | "
        f"{INR_SYMBOL} {prices['gold_22k_10gram']:.2f} (10g)\n"
        f"  (c) 18k: {INR_SYMBOL} {prices['gold_18k_per_gram']:.2f} per gram | "
        f"{INR_SYMBOL} {prices['gold_18k_8gram']:.2f} (8g) | "
        f"{INR_SYMBOL} {prices['gold_18k_10gram']:.2f} (10g)\n\n"
        f"2. SILVER\n"
        f"  (a) Silver (per Gram): {INR_SYMBOL} {prices['silver_per_gram']:.2f}\n"
        f"  (b) Silver (per Kg): {INR_SYMBOL} {prices['silver_per_kg']:.2f}\n\n"
        f"Regards,\n{sender_name}"
    )
    msg.set_content(text_content)

    # HTML version
    html_content = f"""
    <html>
        <body>
            <p>Hi {recipient_name},</p>
            <h3>Today's Gold & Silver Prices</h3>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>1g</th>
                        <th>8g</th>
                        <th>10g</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Gold 24k</td>
                        <td>{INR_SYMBOL} {prices["gold_24k_per_gram"]:.2f}</td>
                        <td>{INR_SYMBOL} {prices["gold_24k_8gram"]:.2f}</td>
                        <td>{INR_SYMBOL} {prices["gold_24k_10gram"]:.2f}</td>
                    </tr>
                    <tr>
                        <td>Gold 22k</td>
                        <td>{INR_SYMBOL} {prices["gold_22k_per_gram"]:.2f}</td>
                        <td>{INR_SYMBOL} {prices["gold_22k_8gram"]:.2f}</td>
                        <td>{INR_SYMBOL} {prices["gold_22k_10gram"]:.2f}</td>
                    </tr>
                    <tr>
                        <td>Gold 18k</td>
                        <td>{INR_SYMBOL} {prices["gold_18k_per_gram"]:.2f}</td>
                        <td>{INR_SYMBOL} {prices["gold_18k_8gram"]:.2f}</td>
                        <td>{INR_SYMBOL} {prices["gold_18k_10gram"]:.2f}</td>
                    </tr>
                    <tr>
                        <td>Silver (Gram)</td>
                        <td colspan="3">{INR_SYMBOL} {prices["silver_per_gram"]:.2f}</td>
                    </tr>
                    <tr>
                        <td>Silver (Kg)</td>
                        <td colspan="3">{INR_SYMBOL} {prices["silver_per_kg"]:.2f}</td>
                    </tr>
                </tbody>
            </table>
            <p style="margin-top:20px;">Regards,<br>{sender_name}</p>
        </body>
    </html>
    """
    msg.add_alternative(html_content, subtype="html")

    return msg


def main():
    api_key, email_address, email_password = load_credentials()
    sender_name = os.getenv("SENDER_NAME", email_address)
    recipient = os.getenv("RECIPIENT")
    recipient_name = os.getenv("RECIPIENT_NAME")
    rates, date, time = get_gold_silver_rate(api_key)

    gold_price = rates['INRXAU']
    silver_price = rates['INRXAG']

    prices = compute_prices(gold_price, silver_price)

    save_gold_silver_rates(CSV_FILE, date, time, prices)

    try:
        smtp = login_to_email(email_address, email_password)
        msg = create_email(prices, sender_name, recipient, recipient_name)
        smtp.send_message(msg)
        print("Email sent successfully!")
        smtp.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    main()
