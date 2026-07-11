import anthropic


SEO_PROMPT = """You are an SEO content strategist specializing in US immigration topics.

Rewrite the article below for maximum SEO performance. Target readers are immigrants, visa applicants, and immigration lawyers searching on Google.

Original Title: {title}
Source: {url}
Target Keywords to use naturally throughout the article:
{keywords_block}
Content:
{content}

Rules for keyword usage:
- Primary keyword (first in list) must appear in the title, first paragraph, and at least 2 H2s
- All 5 keywords should appear at least once in the body
- Do NOT stuff keywords — integrate them naturally

Output your response using EXACTLY these delimiters (no extra text before or after each value):

===SEO_TITLE===
(SEO-optimized title, 55–60 characters, include primary keyword naturally)
===META_DESC===
(Compelling meta description, 150–160 characters, include a call-to-action)
===FOCUS_KEYWORD===
(The single most important keyword from the target list)
===CONTENT===
(Full rewritten article in markdown. 800–1000 words. Include: intro paragraph, 3–4 H2 sections, bullet points where helpful, and an ## FAQ section with 3 real questions people search for.)
===END==="""


def _extract(raw: str, marker: str, next_marker: str) -> str:
    start = raw.find(f"==={marker}===")
    end = raw.find(f"==={next_marker}===")
    if start == -1 or end == -1:
        return ""
    return raw[start + len(f"==={marker}==="):end].strip()


def rewrite_for_seo(client: anthropic.Anthropic, article: dict, target_keywords: list[str] | None = None) -> dict | None:
    if target_keywords:
        keywords_block = "\n".join(f"{i+1}. {kw}" for i, kw in enumerate(target_keywords))
    else:
        keywords_block = "(none provided — identify the best keyword yourself)"

    prompt = SEO_PROMPT.format(
        title=article["title"],
        url=article["url"],
        keywords_block=keywords_block,
        content=article["content"][:4000],
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text

        seo_title = _extract(raw, "SEO_TITLE", "META_DESC")
        meta_desc = _extract(raw, "META_DESC", "FOCUS_KEYWORD")
        focus_kw = _extract(raw, "FOCUS_KEYWORD", "CONTENT")
        content = _extract(raw, "CONTENT", "END")

        if not seo_title or not content:
            print("  [rewriter] incomplete response, skipped")
            return None

        return {
            "seo_title": seo_title,
            "meta_description": meta_desc,
            "focus_keyword": focus_kw,
            "rewritten_content": content,
        }

    except Exception as e:
        print(f"  [rewriter] API error: {e}")
        return None
