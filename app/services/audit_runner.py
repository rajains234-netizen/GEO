"""
Orchestrates the 5 existing GEO audit scripts into a single pipeline.
Each script outputs JSON to stdout — we capture and combine the results.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from urllib.parse import urlparse

from app.config import get_settings

settings = get_settings()


def run_script(script_name: str, *args, timeout: int = 120) -> dict:
    """Run a Python script from scripts/ and return parsed JSON output."""
    script_path = os.path.join(settings.scripts_dir, script_name)
    cmd = [sys.executable, script_path, *args]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(settings.scripts_dir),
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip(), "script": script_name}
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": f"Script timed out after {timeout}s", "script": script_name}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON output", "script": script_name}
    except Exception as e:
        return {"error": str(e), "script": script_name}


def extract_brand_name(url: str, page_data: dict) -> str:
    """Extract brand name from page data or URL."""
    title = page_data.get("title", "")
    if title:
        # Use first part of title before separators
        for sep in [" | ", " - ", " — ", " – ", " :: "]:
            if sep in title:
                return title.split(sep)[0].strip()
        return title.strip()
    # Fallback to domain name
    domain = urlparse(url).netloc.replace("www.", "")
    return domain.split(".")[0].capitalize()


def compute_scores(page_data: dict, citability: dict, brand_data: dict, llms_data: dict) -> dict:
    """Compute GEO category scores from raw analysis data."""

    # AI Citability (0-100)
    citability_score = citability.get("overall_score", 50)
    if "error" in citability:
        citability_score = 40

    # Brand Authority (0-100)
    brand_score = brand_data.get("overall_score", 50)
    if "error" in brand_data:
        brand_score = 40

    # Technical (0-100) — from page data
    tech_score = 70  # base
    security = page_data.get("security_headers", {})
    if page_data.get("status_code") == 200:
        tech_score += 5
    if security.get("https"):
        tech_score += 5
    if security.get("hsts"):
        tech_score += 3
    if security.get("csp"):
        tech_score += 3
    if page_data.get("ssr_detected", True):
        tech_score += 5
    else:
        tech_score -= 20
    # robots.txt
    robots = page_data.get("robots_txt", {})
    if robots and not robots.get("error"):
        tech_score += 5
    # llms.txt
    if llms_data.get("found"):
        tech_score += 5
    else:
        tech_score -= 5
    tech_score = max(0, min(100, tech_score))

    # Content E-E-A-T (0-100) — estimate from page data
    eeat_score = 55  # base
    if page_data.get("word_count", 0) > 500:
        eeat_score += 10
    if page_data.get("word_count", 0) > 1500:
        eeat_score += 10
    meta = page_data.get("meta_tags", {})
    if meta.get("description"):
        eeat_score += 5
    if page_data.get("heading_structure"):
        eeat_score += 5
    if page_data.get("structured_data"):
        eeat_score += 10
    eeat_score = max(0, min(100, eeat_score))

    # Schema (0-100)
    schema_score = 30  # base
    structured = page_data.get("structured_data", [])
    if structured:
        schema_score += 20
        schema_types = set()
        for s in structured:
            if isinstance(s, dict):
                schema_types.add(s.get("@type", ""))
        if "Organization" in schema_types or "LocalBusiness" in schema_types:
            schema_score += 20
        if "FAQPage" in schema_types:
            schema_score += 10
        if "Article" in schema_types or "BlogPosting" in schema_types:
            schema_score += 10
        if "Product" in schema_types:
            schema_score += 10
    schema_score = max(0, min(100, schema_score))

    # Platform Optimization (0-100)
    platform_score = 50  # base
    if brand_score > 60:
        platform_score += 10
    if tech_score > 70:
        platform_score += 10
    if llms_data.get("found"):
        platform_score += 10
    if robots and not robots.get("error"):
        platform_score += 5
    platform_score = max(0, min(100, platform_score))

    return {
        "ai_citability": citability_score,
        "brand_authority": brand_score,
        "content_eeat": eeat_score,
        "technical": tech_score,
        "schema": schema_score,
        "platform_optimization": platform_score,
    }


def compute_platform_scores(scores: dict) -> dict:
    """Estimate per-platform readiness from category scores."""
    base = (scores["ai_citability"] + scores["technical"]) / 2
    return {
        "Google AI Overviews": min(100, int(base + scores["schema"] * 0.15)),
        "ChatGPT": min(100, int(base + scores["brand_authority"] * 0.1)),
        "Perplexity": min(100, int(base + scores["content_eeat"] * 0.1)),
        "Gemini": min(100, int(base + scores["schema"] * 0.1)),
        "Bing Copilot": min(100, int(base * 0.9)),
    }


def build_findings(page_data: dict, citability: dict, brand_data: dict, llms_data: dict, scores: dict) -> list:
    """Generate findings list from analysis data."""
    findings = []

    # Technical findings
    robots = page_data.get("robots_txt", {})
    if not robots or robots.get("error"):
        findings.append({
            "severity": "critical",
            "title": "Missing or Invalid robots.txt",
            "description": "No robots.txt file found. AI crawlers have no explicit guidance on what they can access. Create a robots.txt file allowing major AI crawlers (GPTBot, ClaudeBot, PerplexityBot)."
        })

    if not llms_data.get("found"):
        findings.append({
            "severity": "high",
            "title": "No llms.txt File",
            "description": "No llms.txt file found. This emerging standard helps AI systems understand your site. Create one to improve AI discoverability."
        })

    security = page_data.get("security_headers", {})
    if not security.get("https"):
        findings.append({
            "severity": "critical",
            "title": "Site Not Served Over HTTPS",
            "description": "The site does not enforce HTTPS. This is a critical security and trust issue affecting both traditional SEO and AI visibility."
        })

    if not security.get("hsts"):
        findings.append({
            "severity": "medium",
            "title": "Missing HSTS Header",
            "description": "Strict-Transport-Security header not found. Add HSTS to enforce HTTPS connections."
        })

    if not page_data.get("ssr_detected", True):
        findings.append({
            "severity": "critical",
            "title": "Content Requires JavaScript to Render",
            "description": "The page content is rendered client-side. AI crawlers (GPTBot, ClaudeBot, PerplexityBot) do NOT execute JavaScript and will see an empty page. Implement server-side rendering."
        })

    # Citability findings
    if scores["ai_citability"] < 50:
        findings.append({
            "severity": "high",
            "title": "Low AI Citability Score",
            "description": f"AI citability score is {scores['ai_citability']}/100. Content lacks self-contained, quotable passages that AI systems can extract and cite. Add answer-first content blocks, statistics, and structured explanations."
        })

    # Schema findings
    if scores["schema"] < 50:
        findings.append({
            "severity": "high",
            "title": "Insufficient Structured Data",
            "description": f"Schema score is {scores['schema']}/100. Add Organization, LocalBusiness, FAQ, or relevant schema types to help AI systems understand your content."
        })

    # Brand findings
    if scores["brand_authority"] < 50:
        findings.append({
            "severity": "medium",
            "title": "Weak Brand Authority Signals",
            "description": f"Brand authority score is {scores['brand_authority']}/100. Build presence on platforms AI models rely on: YouTube, Reddit, Wikipedia, LinkedIn."
        })

    # Content findings
    word_count = page_data.get("word_count", 0)
    if word_count < 300:
        findings.append({
            "severity": "high",
            "title": "Thin Homepage Content",
            "description": f"Homepage has only {word_count} words. AI systems need substantial content to extract and cite. Expand to 1000+ words with detailed, authoritative information."
        })

    meta = page_data.get("meta_tags", {})
    if not meta.get("description"):
        findings.append({
            "severity": "medium",
            "title": "Missing Meta Description",
            "description": "No meta description found. Add a compelling 150-160 character description that AI systems can use for page summaries."
        })

    return findings


def build_action_items(findings: list, scores: dict) -> tuple:
    """Generate quick wins, medium-term, and strategic action items."""
    quick_wins = []
    medium_term = []
    strategic = []

    for f in findings:
        if f["severity"] == "critical":
            quick_wins.append(f"Fix: {f['title']} — {f['description'][:100]}...")
        elif f["severity"] == "high":
            medium_term.append(f"Address: {f['title']} — {f['description'][:100]}...")
        else:
            strategic.append(f"Optimize: {f['title']} — {f['description'][:100]}...")

    # Ensure minimum items
    if not quick_wins:
        quick_wins.append("Review and optimize meta descriptions for AI snippet readiness")
    if not medium_term:
        medium_term.append("Create FAQ content with FAQPage schema for common industry questions")
    if not strategic:
        strategic.append("Build thought leadership content for high AI citability")

    return quick_wins[:5], medium_term[:5], strategic[:5]


def build_crawler_access(page_data: dict) -> dict:
    """Build crawler access map from robots.txt data."""
    robots = page_data.get("robots_txt", {})
    crawlers_map = robots.get("ai_crawlers", {})

    default_crawlers = {
        "GPTBot": {"platform": "ChatGPT / OpenAI", "status": "No Directive", "recommendation": "Allow for AI visibility"},
        "ClaudeBot": {"platform": "Claude / Anthropic", "status": "No Directive", "recommendation": "Allow for AI visibility"},
        "PerplexityBot": {"platform": "Perplexity AI", "status": "No Directive", "recommendation": "Allow for AI visibility"},
        "Googlebot": {"platform": "Google Search + AI Overviews", "status": "No Directive", "recommendation": "Keep allowed"},
        "Bingbot": {"platform": "Bing Copilot + ChatGPT", "status": "No Directive", "recommendation": "Keep allowed"},
        "Google-Extended": {"platform": "Gemini / Google AI", "status": "No Directive", "recommendation": "Allow for AI training visibility"},
    }

    if crawlers_map:
        for crawler, info in crawlers_map.items():
            if crawler in default_crawlers:
                status = "Allowed" if info.get("allowed", True) else "Blocked"
                default_crawlers[crawler]["status"] = status
                if status == "Blocked":
                    default_crawlers[crawler]["recommendation"] = "Unblock for AI visibility"
                else:
                    default_crawlers[crawler]["recommendation"] = "Keep allowed"

    return default_crawlers


def run_full_audit(url: str, output_dir: str, progress_callback=None) -> dict:
    """
    Run the complete GEO audit pipeline with Claude AI analysis and generate a PDF report.

    Pipeline:
    1. Collect raw data via Python scripts (fetch_page, citability_scorer, brand_scanner, llmstxt_generator)
    2. Send raw data to Claude API for deep analysis (citability, E-E-A-T, platforms, schema)
    3. Claude generates the full client report with tailored recommendations
    4. Extract scores and findings from Claude's analysis
    5. Generate PDF from the enriched data

    Args:
        url: The website URL to audit
        output_dir: Directory to save output files
        progress_callback: Optional function(message) to report progress

    Returns:
        dict with pdf_path, geo_score, audit_json, and full_report
    """
    os.makedirs(output_dir, exist_ok=True)

    def update(msg):
        if progress_callback:
            progress_callback(msg)

    # =====================================================================
    # PHASE 1: Collect raw data via Python scripts
    # =====================================================================

    update("Fetching and analyzing website...")
    page_data = run_script("fetch_page.py", url, "full", timeout=60)

    update("Extracting content blocks...")
    content_blocks = run_script("fetch_page.py", url, "blocks", timeout=60)

    update("Scoring AI citability...")
    citability = run_script("citability_scorer.py", url, timeout=60)

    update("Scanning brand authority signals...")
    brand_name = extract_brand_name(url, page_data)
    domain = urlparse(url).netloc.replace("www.", "")
    brand_data = run_script("brand_scanner.py", brand_name, domain, timeout=60)

    update("Checking llms.txt and AI crawler access...")
    llms_data = run_script("llmstxt_generator.py", url, "validate", timeout=30)

    # Compute baseline scores from scripts
    scores = compute_scores(page_data, citability, brand_data, llms_data)
    crawler_access = build_crawler_access(page_data)

    # =====================================================================
    # PHASE 2: Claude AI deep analysis (same quality as Claude Code)
    # =====================================================================

    claude_analysis = None
    full_report_md = None

    if settings.anthropic_api_key:
        try:
            from app.services.claude_analyzer import run_full_claude_analysis

            update("AI analyzing your website (this is the detailed part)...")
            claude_analysis = run_full_claude_analysis(
                url=url,
                page_data=page_data,
                content_blocks=content_blocks,
                brand_data=brand_data,
                llms_data=llms_data,
                technical_scores=scores,
                crawler_access=crawler_access,
                progress_callback=update,
            )

            full_report_md = claude_analysis.get("full_report", "")

            # Save the full markdown report
            report_md_path = os.path.join(output_dir, "GEO-CLIENT-REPORT.md")
            with open(report_md_path, "w", encoding="utf-8") as f:
                f.write(full_report_md)

        except Exception as e:
            update(f"AI analysis encountered an issue, using script-based analysis...")
            print(f"Claude analysis error: {e}")

    # =====================================================================
    # PHASE 3: Build audit JSON for PDF generation
    # =====================================================================

    update("Computing final GEO scores...")

    geo_score = int(
        scores["ai_citability"] * 0.25
        + scores["brand_authority"] * 0.20
        + scores["content_eeat"] * 0.20
        + scores["technical"] * 0.15
        + scores["schema"] * 0.10
        + scores["platform_optimization"] * 0.10
    )

    findings = build_findings(page_data, citability, brand_data, llms_data, scores)
    quick_wins, medium_term, strategic = build_action_items(findings, scores)

    # Use Claude's executive summary if available, otherwise generate basic one
    if full_report_md and len(full_report_md) > 200:
        # Extract executive summary from Claude's report (first paragraph after ## Executive Summary)
        exec_summary = ""
        lines = full_report_md.split("\n")
        capture = False
        for line in lines:
            if "executive summary" in line.lower() and "#" in line:
                capture = True
                continue
            if capture and line.startswith("#"):
                break
            if capture and line.strip():
                exec_summary += line.strip() + " "
        executive_summary = exec_summary.strip() if exec_summary.strip() else (
            f"{brand_name} achieves a GEO Score of {geo_score}/100. "
            f"See the full report for detailed analysis and recommendations."
        )
    else:
        executive_summary = (
            f"{brand_name} achieves a GEO Score of {geo_score}/100. "
            f"AI Citability scores {scores['ai_citability']}/100, "
            f"Brand Authority {scores['brand_authority']}/100, "
            f"Content E-E-A-T {scores['content_eeat']}/100, "
            f"Technical foundations {scores['technical']}/100, "
            f"Schema markup {scores['schema']}/100, "
            f"and Platform Optimization {scores['platform_optimization']}/100. "
            f"{'Critical issues require immediate attention.' if any(f['severity'] == 'critical' for f in findings) else 'No critical issues found, but optimization opportunities exist.'}"
        )

    audit_json = {
        "url": url,
        "brand_name": brand_name,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "geo_score": geo_score,
        "scores": scores,
        "platforms": compute_platform_scores(scores),
        "executive_summary": executive_summary,
        "findings": findings,
        "quick_wins": quick_wins,
        "medium_term": medium_term,
        "strategic": strategic,
        "crawler_access": crawler_access,
    }

    # =====================================================================
    # PHASE 4: Generate outputs
    # =====================================================================

    # Write JSON
    json_path = os.path.join(output_dir, "audit_data.json")
    with open(json_path, "w") as f:
        json.dump(audit_json, f, indent=2, default=str)

    # Generate PDF
    update("Generating professional PDF report...")
    pdf_path = os.path.join(output_dir, "GEO-REPORT.pdf")
    run_script("generate_pdf_report.py", json_path, pdf_path, timeout=60)

    return {
        "pdf_path": pdf_path,
        "geo_score": geo_score,
        "audit_json": audit_json,
        "full_report": full_report_md,
    }
