import json
import anthropic


KEYWORD_PROMPT = """You are an SEO keyword researcher specializing in US immigration content.

Analyze the article below and identify exactly 5 high-value target keywords for SEO.

Article Title: {title}
Article URL: {url}
Content excerpt:
{content}

Rules:
- Keywords should be 2–5 words (long-tail preferred)
- Mix of informational and commercial intent
- Must be specific to this article's topic (not generic like "immigration news")
- Think about what people actually type into Google when looking for this information
- Order from highest search intent / relevance to lowest

Return ONLY a valid JSON array of exactly 5 strings. No explanations, no markdown:
["keyword one", "keyword two", "keyword three", "keyword four", "keyword five"]"""


def analyze_keywords(client: anthropic.Anthropic, article: dict) -> list[str]:
    prompt = KEYWORD_PROMPT.format(
        title=article["title"],
        url=article["url"],
        content=article["content"][:2000],
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()

        start = raw.find("[")
        end = raw.rfind("]") + 1
        keywords = json.loads(raw[start:end])

        # Ensure exactly 5, strings only
        keywords = [str(k).strip() for k in keywords if k][:5]
        return keywords

    except Exception as e:
        print(f"  [keywords] analysis failed: {e}")
        return []
