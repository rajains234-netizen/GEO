"""
Claude AI-powered GEO analysis service.

Replicates the exact same analysis that Claude Code skills produce:
- AI Citability scoring with rewrite suggestions
- Content E-E-A-T deep evaluation
- Platform-specific optimization analysis
- Schema audit with JSON-LD generation
- Full client-ready report with tailored recommendations

Each function sends the raw data + the same prompts used by the GEO skills
to Claude API and returns structured analysis.
"""

import json
from typing import Optional

import anthropic

from app.config import get_settings

settings = get_settings()


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
    """Call Claude API and return the text response."""
    client = get_client()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# 1. AI CITABILITY ANALYSIS
# ---------------------------------------------------------------------------

CITABILITY_SYSTEM = """You are an AI citability specialist. You analyze web content to determine how likely AI systems (ChatGPT, Claude, Perplexity, Gemini) are to cite or quote passages from the page.

Research shows optimal AI-cited passages are:
- 134-167 words long
- Self-contained (extractable without context)
- Fact-rich with specific statistics
- Structured with clear answer patterns ("X is...", definition patterns)
- Definition patterns increase citation by 2.1x
- Statistics increase citation by 40%
- Authority quotes increase by 115%

Score every major content block on these 5 dimensions:
1. Answer Block Quality (30%): Does passage directly answer a question in 1-2 sentences? Quotable verbatim?
2. Self-Containment (25%): Understandable without surrounding context? Defines own terms?
3. Structural Readability (20%): Clear formatting? Lists, tables, bold terms? Scannable?
4. Statistical Density (15%): Specific numbers, dates, percentages, measurable claims?
5. Uniqueness (10%): Original data, proprietary insights, perspectives not found elsewhere?

You must provide specific rewrite suggestions for weak passages."""


def analyze_citability(page_data: dict, content_blocks: dict) -> str:
    """Deep AI citability analysis with rewrite suggestions."""
    prompt = f"""Analyze this website's content for AI citability.

URL: {page_data.get('url', 'Unknown')}
Title: {page_data.get('title', 'Unknown')}
Word Count: {page_data.get('word_count', 0)}

Content blocks (heading + text):
{json.dumps(content_blocks.get('blocks', [])[:20], indent=2, default=str)}

Provide:
1. **Overall Citability Score (0-100)** with score for each of the 5 dimensions
2. **Top 3 Most Citable Passages** — quote them and explain why they work
3. **Top 3 Weakest Passages** — quote them and provide specific REWRITE suggestions that would make them citable (show before/after)
4. **Page-Level Assessment** — what type of questions could AI cite this page for?
5. **Quick Wins** — 5 specific changes to increase citability, with estimated citability lift percentage

Format as clean markdown with scores and specific examples from the actual content."""

    return call_claude(CITABILITY_SYSTEM, prompt, max_tokens=3000)


# ---------------------------------------------------------------------------
# 2. CONTENT E-E-A-T ANALYSIS
# ---------------------------------------------------------------------------

EEAT_SYSTEM = """You are a content quality and E-E-A-T specialist for GEO (Generative Engine Optimization).

Evaluate content across Google's E-E-A-T framework:
- Experience (0-25): Original research, case studies, first-hand accounts, process documentation
- Expertise (0-25): Author credentials, technical depth, methodology transparency, Person schema
- Authoritativeness (0-25): External citations, industry recognition, institutional backing, domain authority
- Trustworthiness (0-25): HTTPS, privacy policy, contact info, editorial standards, transparent sourcing

Also assess:
- Content freshness and update signals
- AI content indicators (generic patterns, lack of specificity, formulaic structure)
- Topical authority (depth and breadth of coverage)
- Readability (Flesch score estimate, paragraph length, heading structure)

Be specific. Reference actual content from the page. Don't give generic advice — tailor everything to this exact website."""


def analyze_eeat(page_data: dict, content_blocks: dict) -> str:
    """Deep E-E-A-T content quality analysis."""
    # Build content summary
    headings = page_data.get('heading_structure', [])
    meta_desc = page_data.get('description', '')
    structured_data = page_data.get('structured_data', [])

    prompt = f"""Analyze this website's content quality and E-E-A-T signals.

URL: {page_data.get('url', 'Unknown')}
Title: {page_data.get('title', 'Unknown')}
Meta Description: {meta_desc}
Word Count: {page_data.get('word_count', 0)}
H1 Tags: {page_data.get('h1_tags', [])}
Heading Structure: {json.dumps(headings[:30], default=str)}
Structured Data Types: {[s.get('@type', 'unknown') for s in structured_data if isinstance(s, dict)]}

Content blocks:
{json.dumps(content_blocks.get('blocks', [])[:15], indent=2, default=str)}

Provide:
1. **E-E-A-T Score Breakdown** — score each dimension (0-25) with specific evidence from the page
   - Experience: What first-hand experience signals exist?
   - Expertise: Are there author credentials, technical depth?
   - Authoritativeness: External recognition signals?
   - Trustworthiness: Privacy, contact, sourcing signals?
2. **Content Quality Score (0-100)** with the weighted formula
3. **AI Content Assessment** — does this read like human-written, AI-assisted, or AI-generated? Why?
4. **Specific Improvements** — 5 concrete actions to improve E-E-A-T, tailored to this site's content
5. **Author/Credential Recommendations** — what credentials should be displayed and where?

Format as clean markdown."""

    return call_claude(EEAT_SYSTEM, prompt, max_tokens=3000)


# ---------------------------------------------------------------------------
# 3. PLATFORM-SPECIFIC OPTIMIZATION
# ---------------------------------------------------------------------------

PLATFORM_SYSTEM = """You are an AI search platform optimization specialist. You analyze websites for readiness across 5 major AI platforms:

1. Google AI Overviews: Values question-answer headings, 40-60 word answer blocks, tables, lists, schema markup, already-ranking content
2. ChatGPT Web Search: Values entity recognition (Wikipedia, Wikidata, sameAs), factual/concise content, statistics with sources, expert attribution
3. Perplexity AI: Values community validation (Reddit, forums), primary source data, content freshness, visible dates
4. Google Gemini: Values Google ecosystem presence (YouTube, Business Profile, Scholar), Knowledge Graph signals, long-form comprehensive content
5. Bing Copilot: Values IndexNow protocol, Bing Webmaster Tools, professional tone, LinkedIn presence, Microsoft ecosystem

Score each platform 0-100 and provide platform-specific action items."""


def analyze_platforms(page_data: dict, brand_data: dict, content_blocks: dict) -> str:
    """Platform-specific optimization analysis."""
    robots = page_data.get('robots_txt', {})
    crawlers = robots.get('ai_crawlers', {})

    prompt = f"""Analyze this website's readiness for each AI search platform.

URL: {page_data.get('url', 'Unknown')}
Title: {page_data.get('title', 'Unknown')}
Word Count: {page_data.get('word_count', 0)}
Structured Data: {[s.get('@type', 'unknown') for s in page_data.get('structured_data', []) if isinstance(s, dict)]}
AI Crawler Access: {json.dumps(crawlers, default=str)}
Brand Presence: {json.dumps(brand_data, indent=2, default=str)[:2000]}

Content sample (first 10 blocks):
{json.dumps(content_blocks.get('blocks', [])[:10], indent=2, default=str)}

For each of the 5 platforms provide:
1. **Score (0-100)** with breakdown by signal category
2. **What's working** — specific strengths for that platform
3. **What's missing** — specific gaps
4. **Top 3 actions** — concrete steps to improve visibility on that platform

Then provide:
- **Cross-Platform Synergies** — actions that improve multiple platforms at once
- **Platform Priority Ranking** — which platforms to focus on first for this specific business

Format as clean markdown with a summary table at the top."""

    return call_claude(PLATFORM_SYSTEM, prompt, max_tokens=4000)


# ---------------------------------------------------------------------------
# 4. SCHEMA & STRUCTURED DATA ANALYSIS
# ---------------------------------------------------------------------------

SCHEMA_SYSTEM = """You are a Schema.org structured data specialist focused on AI discoverability.

Critical schemas for GEO:
- Organization/LocalBusiness with sameAs (links to Wikipedia, LinkedIn, YouTube, etc.)
- Person schema for authors (name, jobTitle, sameAs, knowsAbout)
- Article schema (headline, author as Person, datePublished, dateModified)
- speakable property (helps voice assistants cite content)
- WebSite + SearchAction (sitelinks search)
- BreadcrumbList (navigation context)
- FAQPage (RESTRICTED since Aug 2023 — only government and health sites)
- HowTo (REMOVED since Sept 2023 — do NOT recommend)

sameAs is the SINGLE most impactful property for GEO — it connects your entity across platforms.

Always generate ready-to-use JSON-LD code that the site can copy-paste."""


def analyze_schema(page_data: dict) -> str:
    """Schema audit with JSON-LD generation."""
    structured = page_data.get('structured_data', [])

    prompt = f"""Audit this website's structured data and generate missing schemas.

URL: {page_data.get('url', 'Unknown')}
Title: {page_data.get('title', 'Unknown')}

Existing structured data found:
{json.dumps(structured, indent=2, default=str)[:3000]}

Provide:
1. **Schema Score (0-100)** with breakdown:
   - Organization/LocalBusiness (0-20)
   - Article/content schema (0-15)
   - Person schema for authors (0-15)
   - sameAs completeness (0-15)
   - speakable property (0-10)
   - BreadcrumbList (0-5)
   - WebSite + SearchAction (0-5)
   - No deprecated schemas (0-5)
   - JSON-LD format (0-5)
   - Validation (0-5)

2. **Existing Schema Assessment** — what's correct, what's incomplete, any errors

3. **Missing Schema Opportunities** — what should be added

4. **Generated JSON-LD** — provide COMPLETE, ready-to-paste JSON-LD code blocks for:
   - Organization (with sameAs placeholders for major platforms)
   - Any other schemas relevant to this site type

5. **Priority Actions** — ranked by GEO impact

Format as clean markdown with JSON-LD in code blocks."""

    return call_claude(SCHEMA_SYSTEM, prompt, max_tokens=4000)


# ---------------------------------------------------------------------------
# 5. FULL CLIENT REPORT SYNTHESIS
# ---------------------------------------------------------------------------

REPORT_SYSTEM = """You are a GEO (Generative Engine Optimization) report writer creating a professional, client-ready audit report.

Tone:
- Professional but accessible (for business owners, not developers)
- Confident and direct (state as conclusions, not possibilities)
- Action-oriented (every finding connects to a specific action)
- Business-impact focused (translate technical to dollar estimates)
- Avoid jargon without explanation, hedging, passive voice

Impact framing:
- AI search projected to be 25-40% of organic traffic by end 2026
- 10-point GEO improvement = roughly 15-25% citation frequency increase
- Connect recommendations to business value

GEO Score Formula:
GEO_Score = (Citability × 0.25) + (Brand × 0.20) + (EEAT × 0.20) + (Technical × 0.15) + (Schema × 0.10) + (Platform × 0.10)

Score Interpretation:
- 85-100: Excellent
- 70-84: Good
- 55-69: Moderate
- 40-54: Below Average
- 0-39: Needs Attention"""


def generate_full_report(
    url: str,
    page_data: dict,
    citability_analysis: str,
    eeat_analysis: str,
    platform_analysis: str,
    schema_analysis: str,
    brand_data: dict,
    technical_scores: dict,
    crawler_access: dict,
    llms_data: dict,
) -> str:
    """Generate the complete client-ready GEO report."""

    prompt = f"""Generate a comprehensive, client-ready GEO Audit Report for this website.

## Raw Data

**URL:** {url}
**Page Title:** {page_data.get('title', 'Unknown')}
**Meta Description:** {page_data.get('description', '')}
**Word Count:** {page_data.get('word_count', 0)}

## AI Citability Analysis
{citability_analysis}

## Content E-E-A-T Analysis
{eeat_analysis}

## Platform Optimization Analysis
{platform_analysis}

## Schema & Structured Data Analysis
{schema_analysis}

## Brand Presence Data
{json.dumps(brand_data, indent=2, default=str)[:2000]}

## Technical Scores
{json.dumps(technical_scores, indent=2, default=str)}

## AI Crawler Access
{json.dumps(crawler_access, indent=2, default=str)}

## llms.txt Status
{json.dumps(llms_data, indent=2, default=str)[:500]}

---

Generate the FULL client report with these sections:

1. **Executive Summary** — 1 paragraph: scope, overall GEO score, top finding, top 3 recs
2. **GEO Readiness Score** — weighted breakdown table with all 6 categories
3. **AI Visibility Dashboard** — per-platform readiness table (Google AIO, ChatGPT, Perplexity, Gemini, Bing Copilot)
4. **AI Crawler Access Status** — table for all major bots with Allow/Block status
5. **Brand Authority Analysis** — platform presence table with AI impact assessment
6. **Citability Analysis** — top 5 most citable pages/passages and top 5 weakest with specific rewrites
7. **Technical Health Summary** — Core Web Vitals, SSR, mobile, security, speed
8. **Schema & Structured Data** — what exists, what's missing, generated JSON-LD
9. **llms.txt Status** — present/absent, recommendations
10. **Prioritized Action Plan:**
    - Quick Wins (This Week, <4 hours each)
    - Medium-Term (This Month, 1-5 days each)
    - Strategic (This Quarter, weeks/months)
11. **Appendix** — methodology, glossary

Make the report 3,000-5,000 words. Be specific to THIS website — reference actual content, actual pages, actual issues found. No generic advice.

Format as clean markdown."""

    return call_claude(REPORT_SYSTEM, prompt, max_tokens=8000)


# ---------------------------------------------------------------------------
# ORCHESTRATOR — Runs all 5 analyses and synthesizes
# ---------------------------------------------------------------------------

def run_full_claude_analysis(
    url: str,
    page_data: dict,
    content_blocks: dict,
    brand_data: dict,
    llms_data: dict,
    technical_scores: dict,
    crawler_access: dict,
    progress_callback=None,
) -> dict:
    """
    Run all Claude-powered analyses and generate the full report.

    Returns dict with:
        - citability_analysis: str
        - eeat_analysis: str
        - platform_analysis: str
        - schema_analysis: str
        - full_report: str (the complete client-ready report)
        - scores: dict (extracted scores)
    """

    def update(msg):
        if progress_callback:
            progress_callback(msg)

    # Run the 4 category analyses
    update("AI analyzing citability and content quality...")
    citability_analysis = analyze_citability(page_data, content_blocks)

    update("AI evaluating E-E-A-T signals...")
    eeat_analysis = analyze_eeat(page_data, content_blocks)

    update("AI assessing platform-specific optimization...")
    platform_analysis = analyze_platforms(page_data, brand_data, content_blocks)

    update("AI auditing schema and structured data...")
    schema_analysis = analyze_schema(page_data)

    # Generate the full client report
    update("AI writing your personalized GEO report...")
    full_report = generate_full_report(
        url=url,
        page_data=page_data,
        citability_analysis=citability_analysis,
        eeat_analysis=eeat_analysis,
        platform_analysis=platform_analysis,
        schema_analysis=schema_analysis,
        brand_data=brand_data,
        technical_scores=technical_scores,
        crawler_access=crawler_access,
        llms_data=llms_data,
    )

    return {
        "citability_analysis": citability_analysis,
        "eeat_analysis": eeat_analysis,
        "platform_analysis": platform_analysis,
        "schema_analysis": schema_analysis,
        "full_report": full_report,
    }
