"""Push Science CSV to Google Sheet 'Science' tab.

Usage:
    python scripts/push_to_gsheet.py

Requires:
    - bright-fastness-397410-e569326fd692.json (service account)
    - gspread and google-auth packages
"""
import csv
import json
import os
import sys

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Run: pip install gspread google-auth")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
CREDS_PATH = os.path.join(ROOT, "bright-fastness-397410-e569326fd692.json")
CSV_PATH = os.path.join(ROOT, "output", "Secondary (BV)-2026_Class 9-10_Science_compressed.csv")
SHEET_KEY = "11I4QaFd1GZSaFWFCQ9I7UuBBAUpfxZ-jN1y9TZGkmV0"
WORKSHEET_NAME = "Science"


def main():
    # Verify files exist
    if not os.path.exists(CREDS_PATH):
        print(f"ERROR: Service account not found: {CREDS_PATH}")
        sys.exit(1)
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: CSV not found: {CSV_PATH}")
        sys.exit(1)

    # Load credentials
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=scopes)
    client = gspread.authorize(creds)

    # Open sheet
    print(f"Opening sheet: {SHEET_KEY}")
    sheet = client.open_by_key(SHEET_KEY)

    # Get or create worksheet
    try:
        worksheet = sheet.worksheet(WORKSHEET_NAME)
        print(f"Found worksheet: {WORKSHEET_NAME}")
    except gspread.WorksheetNotFound:
        print(f"Creating worksheet: {WORKSHEET_NAME}")
        worksheet = sheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=10)

    # Read CSV
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)

    print(f"Read {len(rows)} rows from CSV (including header)")

    # Clear existing data
    worksheet.clear()
    print("Cleared existing data")

    # Update with new data
    worksheet.update(range_name="A1", values=rows)
    print(f"Updated worksheet with {len(rows)} rows")

    # Format header row
    worksheet.format("A1:F1", {
        "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.7},
        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True}
    })
    print("Formatted header row")

    print(f"\nDone! Sheet: https://docs.google.com/spreadsheets/d/{SHEET_KEY}")


if __name__ == "__main__":
    main()
