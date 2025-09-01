import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =====================
# GOOGLE SHEETS SETUP
# =====================
# Load credentials from GitHub Secret
creds_json = os.environ["GOOGLE_CREDENTIALS"]
creds_dict = json.loads(creds_json)

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open target Google Sheet
SPREADSHEET_NAME = "Football Predictions"
sheet = client.open(SPREADSHEET_NAME).sheet1


# =====================
# SCRAPING FUNCTION
# =====================
def scrape_predictions(url, source_name):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    predictions = []

    # SportyTrader prediction cards
    matches = soup.select("div.card")

    for match in matches[:100]:  # only first 100 predictions
        try:
            teams = match.select_one("div.tip-title").get_text(strip=True)
        except:
            teams = "N/A"
        try:
            prediction = match.select_one("div.tip-content").get_text(strip=True)
        except:
            prediction = "N/A"
        try:
            date_time = match.select_one("div.tip-match-time").get_text(strip=True)
        except:
            date_time = "N/A"

        predictions.append([source_name, teams, prediction, date_time])

    return predictions


# =====================
# MAIN JOB
# =====================
def main():
    print("🔎 Scraping predictions...")

    # Scrape both links
    data1 = scrape_predictions("https://www.sportytrader.com/en/betting-tips/football/over-under/", "Over/Under")
    data2 = scrape_predictions("https://www.sportytrader.com/en/betting-tips/football/double-chance/", "Double Chance")

    # Clear sheet and write new data
    sheet.clear()
    sheet.append_row(["Source", "Match", "Prediction", "Date/Time"])

    for row in data1 + data2:
        sheet.append_row(row)

    print("✅ Data updated in Google Sheets!")


if __name__ == "__main__":
    main()
