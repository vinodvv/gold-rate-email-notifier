# Gold Rate Email Notifier

Gold Rate Email Notifier is a Python application that retrieves the latest gold and silver prices using the [MetalPriceAPI](https://metalpriceapi.com/), saves daily prices to a CSV file, and sends a formatted email report to specified recipients using Gmail SMTP.

## Features

- Fetches current gold (24k, 22k, 18k) and silver (per gram, per kg) prices in INR.
- Automatically saves the rates to a CSV file for logging.
- Sends a daily summary email with prices to your chosen recipient.
- Customizable email sender and recipient details.
- Environment variable-based configuration for security and flexibility.

## Requirements

- Python 3.7 or later
- [MetalPriceAPI](https://metalpriceapi.com/) account and API key
- Gmail account and an **app password** (required if using 2-step verification)
- The following Python packages:
    - `requests`
    - `python-dotenv`

## Installation

1. **Clone the repository:**

    ```
    git clone https://github.com/vinodvv/gold-rate-email-notifier.git
    cd gold-rate-email-notifier
    ```

2. **Install dependencies:**

    ```
    pip install -r requirements.txt
    ```

3. **Set up your `.env` file in the project root:**

    ```
    API_KEY=your_metalpriceapi_key
    EMAIL_ADDRESS=your_gmail@gmail.com
    EMAIL_PASSWORD=your_gmail_app_password
    SENDER_NAME=Your Name
    RECIPIENT=recipient@example.com
    RECIPIENT_NAME=Recipient Name
    ```

    - **API_KEY**: Get your free or paid MetalPriceAPI key from https://metalpriceapi.com
    - **EMAIL_ADDRESS**: Your Gmail email address used to send emails.
    - **EMAIL_PASSWORD**: Gmail [app password](https://support.google.com/accounts/answer/185833?hl=en) (never your main password).
    - **RECIPIENT** and **RECIPIENT_NAME**: The target recipient’s email and display name.

4. **Usage**

    Run the script:

    ```
    python gold-rate-email-notifier.py
    ```

    This will fetch rates, append a record to `rates.csv`, and send the summary email.

## Notes

- If you encounter SMTP or login errors, ensure your Gmail account allows [less secure apps](https://support.google.com/accounts/answer/6010255?hl=en) or use an [App Password](https://support.google.com/accounts/answer/185833).
- Daily price logging is enabled in `rates.csv` which will grow over time as a record.
- For automation (e.g., daily cron job), simply schedule the script to run once per day.

## Contributing

Pull requests, issues, and forks are welcome! Please ensure consistent code style and add docstrings/comments where necessary.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

Vinod V V  
[GitHub Profile](https://github.com/vinodvv)

---


