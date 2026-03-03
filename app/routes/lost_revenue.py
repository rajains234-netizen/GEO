"""GET /api/lost-revenue/calculate — 5-layer AI invisibility lost revenue calculator."""

from fastapi import APIRouter, Query

router = APIRouter()

# Voice search conversions are heavily informational; apply a discount to revenue potential
VOICE_CONVERSION_DISCOUNT = 0.5


def calculate_lost_revenue(
    # Search & Discovery
    monthly_search_volume: float = 50000,
    ai_overview_capture_rate: float = 0.35,
    brand_mention_rate: float = 0.10,
    competitor_mention_rate: float = 0.40,
    # Traffic Deflection
    organic_ctr: float = 0.045,
    ctr_reduction: float = 0.30,
    zero_click_rate: float = 0.65,
    # Conversion & Revenue
    avg_order_value: float = 150.0,
    organic_conversion_rate: float = 0.025,
    customer_lifetime_value: float = 450.0,
    repeat_purchase_rate: float = 0.35,
    # Competitive
    num_competitors_in_ai: float = 5,
    market_share_at_risk: float = 0.15,
    competitor_ai_visibility: float = 0.65,
    # AI Channels
    chatbot_referral_potential: float = 0.08,
    voice_search_share: float = 0.20,
    llm_citation_rate: float = 0.05,
) -> dict:
    """Compute the 5-layer attribution model for lost revenue due to AI invisibility."""

    # ── L1: Search Deflection Loss ────────────────────────────────────────────
    # Lost clicks from AI overviews deflecting traffic
    # Searches × AI_Capture% × (1 − Brand_Mention%) × Organic_CTR% × CTR_Reduction%
    l1_lost_clicks = (
        monthly_search_volume
        * ai_overview_capture_rate
        * (1 - brand_mention_rate)
        * organic_ctr
        * ctr_reduction
    )
    l1_lost_revenue = l1_lost_clicks * organic_conversion_rate * avg_order_value

    # ── L2: Zero-Click Impression Loss ───────────────────────────────────────
    # Lost brand impressions in zero-click searches with AI answers
    # Impression_Value × Zero_Click% × AI_Capture% × (1 − Brand_Mention%)
    impression_value_per_search = avg_order_value * organic_conversion_rate * organic_ctr
    l2_lost_revenue = (
        monthly_search_volume
        * impression_value_per_search
        * zero_click_rate
        * ai_overview_capture_rate
        * (1 - brand_mention_rate)
    )

    # ── L3: Competitive Displacement Loss ────────────────────────────────────
    # Market share lost to competitors with higher AI visibility
    # Monthly_Organic_Revenue × Market_Share_At_Risk% × Visibility_Gap
    monthly_organic_revenue = (
        monthly_search_volume * organic_ctr * organic_conversion_rate * avg_order_value
    )
    visibility_gap = max(0.0, competitor_ai_visibility - brand_mention_rate)
    l3_lost_revenue = monthly_organic_revenue * market_share_at_risk * visibility_gap

    # ── L4: AI Channel Loss ───────────────────────────────────────────────────
    # Missed referrals from ChatGPT, Perplexity, voice search
    chatbot_lost = (
        monthly_search_volume
        * chatbot_referral_potential
        * (1 - llm_citation_rate)
        * organic_conversion_rate
        * avg_order_value
    )
    voice_lost = (
        monthly_search_volume
        * voice_search_share
        * (1 - brand_mention_rate)
        * organic_conversion_rate
        * avg_order_value
        * VOICE_CONVERSION_DISCOUNT
    )
    l4_lost_revenue = chatbot_lost + voice_lost
    l4_breakdown = {"chatbot": chatbot_lost, "voice": voice_lost}

    # ── L5: Lifetime Value Cascade ────────────────────────────────────────────
    # Lost repeat purchases from deflected first-time customers
    # Lost_Customers × (CLV − AOV) × Repeat_Rate%
    lost_customers = l1_lost_clicks * organic_conversion_rate
    l5_lost_revenue = lost_customers * (customer_lifetime_value - avg_order_value) * repeat_purchase_rate

    # ── Totals ────────────────────────────────────────────────────────────────
    total_monthly = l1_lost_revenue + l2_lost_revenue + l3_lost_revenue + l4_lost_revenue + l5_lost_revenue
    total_annual = total_monthly * 12
    total_lost_customers = lost_customers

    # ── Model confidence scoring ──────────────────────────────────────────────
    # Penalise confidence when inputs are at default/extreme values
    confidence_factors = [
        min(1.0, monthly_search_volume / 100_000),
        1 - abs(organic_ctr - 0.045) * 5,
        1 - abs(organic_conversion_rate - 0.025) * 10,
        1 - abs(brand_mention_rate - 0.10) * 2,
    ]
    model_confidence = round(max(0.40, min(0.95, sum(confidence_factors) / len(confidence_factors))), 2)

    layer_totals = {
        "l1_search_deflection": round(l1_lost_revenue, 2),
        "l2_zero_click_impression": round(l2_lost_revenue, 2),
        "l3_competitive_displacement": round(l3_lost_revenue, 2),
        "l4_ai_channel": round(l4_lost_revenue, 2),
        "l5_ltv_cascade": round(l5_lost_revenue, 2),
    }

    return {
        "monthly_lost_revenue": round(total_monthly, 2),
        "annual_lost_revenue": round(total_annual, 2),
        "lost_customers_monthly": round(total_lost_customers, 1),
        "market_share_at_risk_pct": round(market_share_at_risk * 100, 1),
        "model_confidence": model_confidence,
        "layers": layer_totals,
        "l4_breakdown": {k: round(v, 2) for k, v in l4_breakdown.items()},
        "inputs_used": {
            "monthly_search_volume": monthly_search_volume,
            "ai_overview_capture_rate": ai_overview_capture_rate,
            "brand_mention_rate": brand_mention_rate,
            "competitor_mention_rate": competitor_mention_rate,
            "organic_ctr": organic_ctr,
            "ctr_reduction": ctr_reduction,
            "zero_click_rate": zero_click_rate,
            "avg_order_value": avg_order_value,
            "organic_conversion_rate": organic_conversion_rate,
            "customer_lifetime_value": customer_lifetime_value,
            "repeat_purchase_rate": repeat_purchase_rate,
            "num_competitors_in_ai": num_competitors_in_ai,
            "market_share_at_risk": market_share_at_risk,
            "competitor_ai_visibility": competitor_ai_visibility,
            "chatbot_referral_potential": chatbot_referral_potential,
            "voice_search_share": voice_search_share,
            "llm_citation_rate": llm_citation_rate,
        },
    }


@router.get("/api/lost-revenue/calculate")
def get_lost_revenue_calculation(
    # Search & Discovery
    monthly_search_volume: float = Query(50000, ge=0, description="Monthly branded + category search volume"),
    ai_overview_capture_rate: float = Query(0.35, ge=0, le=1, description="Fraction of searches captured by AI Overviews"),
    brand_mention_rate: float = Query(0.10, ge=0, le=1, description="Rate at which brand is mentioned in AI answers"),
    competitor_mention_rate: float = Query(0.40, ge=0, le=1, description="Rate at which competitors are mentioned"),
    # Traffic Deflection
    organic_ctr: float = Query(0.045, ge=0, le=1, description="Organic click-through rate"),
    ctr_reduction: float = Query(0.30, ge=0, le=1, description="CTR reduction due to AI Overviews"),
    zero_click_rate: float = Query(0.65, ge=0, le=1, description="Fraction of searches ending without a click"),
    # Conversion & Revenue
    avg_order_value: float = Query(150.0, ge=0, description="Average order value in USD"),
    organic_conversion_rate: float = Query(0.025, ge=0, le=1, description="Organic traffic conversion rate"),
    customer_lifetime_value: float = Query(450.0, ge=0, description="Customer lifetime value in USD"),
    repeat_purchase_rate: float = Query(0.35, ge=0, le=1, description="Repeat purchase rate"),
    # Competitive
    num_competitors_in_ai: float = Query(5, ge=0, description="Number of competitors appearing in AI results"),
    market_share_at_risk: float = Query(0.15, ge=0, le=1, description="Market share at risk from AI displacement"),
    competitor_ai_visibility: float = Query(0.65, ge=0, le=1, description="Average competitor AI visibility score"),
    # AI Channels
    chatbot_referral_potential: float = Query(0.08, ge=0, le=1, description="Chatbot referral potential fraction"),
    voice_search_share: float = Query(0.20, ge=0, le=1, description="Voice search share of total searches"),
    llm_citation_rate: float = Query(0.05, ge=0, le=1, description="Current LLM citation rate for brand"),
):
    """Calculate lost revenue from AI invisibility using a 5-layer attribution model."""
    return calculate_lost_revenue(
        monthly_search_volume=monthly_search_volume,
        ai_overview_capture_rate=ai_overview_capture_rate,
        brand_mention_rate=brand_mention_rate,
        competitor_mention_rate=competitor_mention_rate,
        organic_ctr=organic_ctr,
        ctr_reduction=ctr_reduction,
        zero_click_rate=zero_click_rate,
        avg_order_value=avg_order_value,
        organic_conversion_rate=organic_conversion_rate,
        customer_lifetime_value=customer_lifetime_value,
        repeat_purchase_rate=repeat_purchase_rate,
        num_competitors_in_ai=num_competitors_in_ai,
        market_share_at_risk=market_share_at_risk,
        competitor_ai_visibility=competitor_ai_visibility,
        chatbot_referral_potential=chatbot_referral_potential,
        voice_search_share=voice_search_share,
        llm_citation_rate=llm_citation_rate,
    )
