import json
import anthropic


SEO_PROMPT = """You are an SEO content strategist specializing in US immigration topics.

Rewrite the article below for maximum SEO performance. Target readers are immigrants, visa applicants, and immigration lawyers searching on Google.

Original Title: {title}
Source: {url}
Content:
{content}

Return ONLY a valid JSON object with these exact fields (no markdown, no extra text):
{{
  "seo_title": "SEO-optimized title, 55–60 characters, include focus keyword naturally",
  "meta_description": "Compelling meta description, 150–160 characters, include a call-to-action",
  "focus_keyword": "Primary keyword phrase (2–4 words)",
  "rewritten_content": "Full rewritten article in markdown. 800–1000 words. Include: intro paragraph, 3–4 H2 sections, bullet points where helpful, and an ## FAQ section with 3 real questions people search for."
}}"""


def rewrite_for_seo(client: anthropic.Anthropic, article: dict) -> dict | None:
    prompt = SEO_PROMPT.format(
        title=article["title"],
        url=article["url"],
        content=article["content"][:4000],
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()

        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])

    except json.JSONDecodeError as e:
        print(f"  [rewriter] JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"  [rewriter] API error: {e}")
        return None
