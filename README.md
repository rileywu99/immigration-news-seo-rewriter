# Immigration News SEO Rewriter

Daily automation that scrapes US immigration news via Firecrawl, rewrites each article for SEO using Claude, and pushes the results to Google Sheets.

Runs automatically every day at 8 AM PT via GitHub Actions.

---

## What it does

1. Searches for today's immigration news (USCIS, policy changes, visa updates, etc.)
2. Rewrites each article with Claude: SEO title, meta description, focus keyword, and a full 800–1000 word rewrite with FAQ section
3. Appends each result as a new row in your Google Sheet — skips duplicates automatically

---

## Google Sheet columns

| Column | Field |
|--------|-------|
| A | Date (PT) |
| B | Source domain |
| C | Original URL |
| D | Original Title |
| E | SEO Title (55–60 chars) |
| F | Meta Description (150–160 chars) |
| G | Focus Keyword |
| H | Rewritten Content (markdown) |
| I | Word Count |
| J | Processed At (PT) |

---

## Setup

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/immigration-news-seo-rewriter.git
cd immigration-news-seo-rewriter
pip install -r requirements.txt
```

### 2. Get API keys

| Service | Where to get it |
|---------|----------------|
| Anthropic | https://console.anthropic.com/ |
| Firecrawl | https://firecrawl.dev/ |
| Google Sheets | See step 3 below |

### 3. Set up Google Sheets access

Pick whichever option fits your situation:

#### Option A — Personal Gmail / OAuth (easiest for local dev)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and enable the **Google Sheets API**
2. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
3. Application type: **Desktop app** → download the JSON
4. Save it as `~/.config/gspread/credentials.json`
5. First run will open a browser window asking you to authorize with your Google account — done.

> No need to share the sheet with anyone — you're already the owner.

#### Option B — Service Account (required for GitHub Actions)

1. Go to **IAM & Admin → Service Accounts** → create a service account
2. Download the JSON key → save as `credentials.json` in the project root
3. Set `GOOGLE_SERVICE_ACCOUNT_JSON=credentials.json` in your `.env`
4. **Share the Google Sheet** with the service account email (editor access)
   - The email looks like: `your-sa@your-project.iam.gserviceaccount.com`

### 4. Configure env

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 5. Run locally

```bash
python main.py
```

---

## GitHub Actions (daily automation)

### Add secrets to your repo

Go to **Settings → Secrets and variables → Actions** and add:

| Secret name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | your Anthropic key |
| `FIRECRAWL_API_KEY` | your Firecrawl key |
| `GOOGLE_SHEETS_ID` | `1slKGNB9kHfTdyJk1Q29zdP0XbEIAOcNv3M3h1Oef5Gk` |
| `GOOGLE_CREDENTIALS_JSON_STRING` | the **entire contents** of `credentials.json` as a single line |

> **Tip:** To convert `credentials.json` to a single line for the secret:
> ```bash
> cat credentials.json | tr -d '\n'
> ```

The workflow runs at **8 AM PDT** (UTC+0 15:00). You can also trigger it manually from the Actions tab.

---

## Customize

- **Change news topics** → edit `config/sources.yaml`
- **Change article count** → set `MAX_ARTICLES` in `.env` or the Actions workflow
- **Change schedule** → edit the cron in `.github/workflows/daily_run.yml`
