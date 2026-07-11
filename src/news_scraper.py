import yaml
from pathlib import Path
from firecrawl import FirecrawlApp


def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config" / "sources.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def scrape_immigration_news(api_key: str) -> list[dict]:
    config = load_config()
    queries = config.get("search_queries", [])
    max_articles = config.get("max_articles", 5)
    min_length = config.get("min_content_length", 300)

    app = FirecrawlApp(api_key=api_key)
    articles = []
    seen_urls: set[str] = set()

    for query in queries:
        if len(articles) >= max_articles:
            break
        try:
            result = app.search(query, limit=5)

            # firecrawl-py v4: result.web is a list of SearchResultWeb objects
            items = result.web if hasattr(result, "web") and result.web else []

            for item in items:
                if len(articles) >= max_articles:
                    break

                url = getattr(item, "url", "") or ""
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                title = getattr(item, "title", "") or url
                description = getattr(item, "description", "") or ""

                # Scrape full content for each article
                content = description
                try:
                    scraped = app.scrape_url(url, formats=["markdown"])
                    full_md = getattr(scraped, "markdown", None) or ""
                    if len(full_md) >= min_length:
                        content = full_md
                except Exception as scrape_err:
                    print(f"    [scraper] scrape failed for {url}: {scrape_err}")

                if len(content) < min_length:
                    continue

                source = url.split("/")[2].replace("www.", "") if url else "unknown"
                articles.append({"url": url, "title": title, "content": content, "source": source})

        except Exception as e:
            print(f"  [scraper] query '{query}' failed: {e}")

    return articles
