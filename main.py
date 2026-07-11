import os
import sys
from datetime import datetime

import anthropic
import pytz
from dotenv import load_dotenv

from src.news_scraper import scrape_immigration_news
from src.seo_rewriter import rewrite_for_seo
from src.sheets_exporter import ensure_headers, export_article, get_worksheet

load_dotenv()


def main() -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", "1slKGNB9kHfTdyJk1Q29zdP0XbEIAOcNv3M3h1Oef5Gk")
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials.json")
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON_STRING")

    missing = [k for k, v in {"ANTHROPIC_API_KEY": api_key, "FIRECRAWL_API_KEY": firecrawl_key}.items() if not v]
    if missing:
        print(f"[error] Missing env vars: {', '.join(missing)}")
        sys.exit(1)

    pt_tz = pytz.timezone("America/Los_Angeles")
    today_pt = datetime.now(pt_tz).strftime("%Y-%m-%d")
    print(f"=== Immigration News SEO Rewriter | {today_pt} PT ===\n")

    client = anthropic.Anthropic(api_key=api_key)

    print("Step 1/3  Connecting to Google Sheets...")
    worksheet = get_worksheet(sheet_id, creds_path, creds_json)
    ensure_headers(worksheet)

    print("Step 2/3  Fetching immigration news via Firecrawl...")
    articles = scrape_immigration_news(firecrawl_key)
    print(f"          Found {len(articles)} articles\n")

    print("Step 3/3  Rewriting & exporting...")
    success = 0
    for i, article in enumerate(articles, 1):
        title_preview = article["title"][:65] + "…" if len(article["title"]) > 65 else article["title"]
        print(f"  [{i}/{len(articles)}] {title_preview}")

        seo_data = rewrite_for_seo(client, article)
        if not seo_data:
            print("          → rewrite failed, skipped")
            continue

        export_article(worksheet, today_pt, article, seo_data)
        print(f"          → ✓ exported  ({len(seo_data.get('rewritten_content','').split())} words)")
        success += 1

    print(f"\n=== Done: {success}/{len(articles)} articles written to Sheets ===")


if __name__ == "__main__":
    main()
