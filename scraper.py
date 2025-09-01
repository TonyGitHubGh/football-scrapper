import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==== GOOGLE SHEETS SETUP ====
SHEET_ID = "1c3Bv7NEB_4tQ_BAZZgXcBPe_w9MlhW_B67nAOAA9nCM"
SHEET_NAME = "Sheet1"   # Change if your tab is named differently

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ==== SCRAPER FUNCTION ====
def scrape_predictions(url, source, limit=100):
    predictions = []
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    # Each match block
    blocks = soup.find_all("div", class_="flex flex-col xl:flex-row justify-center items-center border border-primary-grayborder rounded-lg p-2 my-4")
    for block in blocks[:limit]:
        try:
            # Date & League
            date_time = block.find("span", class_="text-xs").text.strip()
            league = block.find("p", class_="py-0").text.strip()

            # Teams
            teams = block.find_all("span", class_="mx-1")
            home = teams[0].text.strip()
            away = teams[1].text.strip()
            match = f"{home} vs {away}"

            # Prediction + Probability
            pred_box = block.find("span", class_="w-full flex justify-center items-center rounded-md font-semibold bg-primary-red text-white mx-1") \
                        or block.find("span", class_="w-full flex justify-center items-center rounded-md font-semibold bg-primary-blue text-white mx-1")
            prediction = pred_box.text.strip() if pred_box else "N/A"

            prob = block.find("span", {"data-trans": "global.probability"})
            probability = prob.text.replace("Probability of", "").strip() if prob else "N/A"

            predictions.append([source, match, prediction, probability, league, date_time])
        except Exception as e:
            print("Error parsing block:", e)
            continue

    return predictions

# ==== MAIN ====
def main():
    all_data = [["Source", "Match", "Prediction", "Probability", "League", "Date/Time"]]

    # Scrape both pages
    over_under_url = "https://www.sportytrader.com/en/betting-tips/football/over-under/"
    double_chance_url = "https://www.sportytrader.com/en/betting-tips/football/double-chance/"

    all_data += scrape_predictions(over_under_url, "Over/Under")
    all_data += scrape_predictions(double_chance_url, "Double Chance")

    # Clear old sheet and update
    sheet.clear()
    sheet.update("A1", all_data)
    print(f"✅ Updated Google Sheet with {len(all_data)-1} predictions at {datetime.now()}")

if __name__ == "__main__":
    main()
