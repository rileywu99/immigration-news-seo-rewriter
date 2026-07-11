import json
import os
from datetime import datetime
from pathlib import Path

import gspread
import pytz
from google.oauth2.service_account import Credentials


SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.readonly"]

HEADERS = [
    "Date (PT)",
    "Source",
    "Original URL",
    "Original Title",
    "Target Keywords (5)",
    "SEO Title",
    "Meta Description",
    "Focus Keyword",
    "Rewritten Content",
    "Word Count",
    "Processed At (PT)",
]


def get_worksheet(sheet_id: str, credentials_path: str | None = None, credentials_json_str: str | None = None):
    """
    Auth priority:
    1. GOOGLE_CREDENTIALS_JSON_STRING env var (GitHub Actions / CI)
    2. credentials_path JSON file (local service account)
    3. gspread OAuth flow (local dev with personal Gmail — opens browser once)
    """
    if credentials_json_str:
        info = json.loads(credentials_json_str)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        gc = gspread.authorize(creds)

    elif credentials_path and Path(credentials_path).exists():
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        gc = gspread.authorize(creds)

    else:
        # OAuth with personal Google account — opens browser on first run, saves token.json locally
        print("  [sheets] No service account found → using OAuth (personal Google account)")
        print("  [sheets] A browser window will open for one-time authorization...")
        gc = gspread.oauth(
            credentials_filename=os.path.join(Path.home(), ".config", "gspread", "credentials.json"),
            authorized_user_filename=os.path.join(Path.home(), ".config", "gspread", "authorized_user.json"),
        )

    return gc.open_by_key(sheet_id).sheet1


def ensure_headers(worksheet) -> None:
    if not worksheet.row_values(1):
        worksheet.append_row(HEADERS)


def is_duplicate(worksheet, url: str) -> bool:
    urls = worksheet.col_values(3)  # Column C = Original URL
    return url in urls


def export_article(worksheet, date_pt: str, article: dict, seo_data: dict, target_keywords: list[str] | None = None) -> None:
    if is_duplicate(worksheet, article["url"]):
        print(f"  [sheets] duplicate skipped: {article['url']}")
        return

    now_pt = datetime.now(pytz.timezone("America/Los_Angeles")).strftime("%Y-%m-%d %H:%M PT")
    word_count = len(seo_data.get("rewritten_content", "").split())
    keywords_str = ", ".join(target_keywords) if target_keywords else seo_data.get("focus_keyword", "")

    row = [
        date_pt,
        article.get("source", ""),
        article.get("url", ""),
        article.get("title", ""),
        keywords_str,                          # Target Keywords (5)
        seo_data.get("seo_title", ""),
        seo_data.get("meta_description", ""),
        target_keywords[0] if target_keywords else seo_data.get("focus_keyword", ""),  # Focus Keyword = #1
        seo_data.get("rewritten_content", ""),
        word_count,
        now_pt,
    ]
    worksheet.append_row(row, value_input_option="USER_ENTERED")
