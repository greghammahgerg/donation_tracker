import requests
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()


ZEFFY_API_KEY = os.getenv("ZEFFY_API_KEY")
GOOGLE_FORM_URL = os.getenv("GOOGLE_FORM_URL")

FORM_ENTRY_IDS = {
    "name": os.getenv("ENTRY_NAME"),
    "amount": os.getenv("ENTRY_AMOUNT"),
    "date": os.getenv("ENTRY_DATE")
}


def get_latest_zeffy_payments():
   
    url = "https://zeffy.com"
    headers = {
        "Authorization": f"Bearer {ZEFFY_API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # Returns the list of payments (adjust dict key based on official payload structure)
        return response.json().get("payments", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Zeffy: {e}")
        return []

def submit_to_google_form(name, amount, date_str):
    """Submits donor details to the Google Form via a POST request."""
    # Convert payment timestamp into a readable date string format
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        formatted_date = dt.strftime("%Y-%m-%d")
    except ValueError:
        formatted_date = date_str

    # Form payload
    form_data = {
        FORM_ENTRY_IDS["name"]: name,
        FORM_ENTRY_IDS["amount"]: f"${amount:.2f}",
        FORM_ENTRY_IDS["date"]: formatted_date
    }

    try:
        response = requests.post(GOOGLE_FORM_URL, data=form_data)
        if response.status_code == 200:
            print(f"Successfully logged donation: {name} - ${amount}")
        else:
            print(f"Failed to submit form. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error submitting to Google Forms: {e}")

def main():
    print("Fetching payments from Zeffy...")
    payments = get_latest_zeffy_payments()
    
    if not payments:
        print("No new payments found or failed to authenticate.")
        return

    # Process each payment in the payload
    for payment in payments:
        # Safeguard dict fetching based on standard Zeffy schemas
        buyer = payment.get("buyer", {})
        first_name = buyer.get("firstName", "")
        last_name = buyer.get("lastName", "")
        full_name = f"{first_name} {last_name}".strip() or "Anonymous"
        
        # Pull amount (convert cents to dollars if Zeffy outputs in smallest currency unit)
        amount_raw = payment.get("amount", 0)
        amount = amount_raw / 100 if isinstance(amount_raw, int) else amount_raw
        
        date_str = payment.get("createdAt", "")

        # Submit data
        submit_to_google_form(full_name, amount, date_str)

if __name__ == "__main__":
    main()
