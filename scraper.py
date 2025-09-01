import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright


# =====================
# GOOGLE SHEETS SETUP
# =====================
creds_json = os.environ["GOOGLE_CREDENTIALS"]
creds_dict = json.loads(creds_json)

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "Football Predictions"
sheet = client.open(SPREADSHEET_NAME).sheet1


# =====================
# SCRAPING FUNCTION
# =====================
def scrape_predictions(url, source_name):
    predictions = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # wait 5s for JS to load
        
        cards = page.locator("div.card").all()
        for card in cards[:100]:
            try:
                teams = card.locator("div.tip-title").inner_text()
            except:
                teams = "N/A"
            try:
                prediction = card.locator("div.tip-content").inner_text()
            except:
                prediction = "N/A"
            try:
                date_time = card.locator("div.tip-match-time").inner_text()
            except:
                date_time = "N/A"

            predictions.append([source_name, teams, prediction, date_time])
        
        browser.close()
    return predictions


# =====================
# MAIN JOB
# =====================
def main():
    print("🔎 Scraping predictions...")

    data1 = scrape_predictions(
        "https://www.sportytrader.com/en/betting-tips/football/over-under/", 
        "Over/Under"
    )
    data2 = scrape_predictions(
        "https://www.sportytrader.com/en/betting-tips/football/double-chance/", 
        "Double Chance"
    )

    # Clear sheet and write new data
    sheet.clear()
    sheet.append_row(["Source", "Match", "Prediction", "Date/Time"])
    for row in data1 + data2:
        sheet.append_row(row)

    print("✅ Data updated in Google Sheets!")


if __name__ == "__main__":
    main()
