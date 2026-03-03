import { useState, useEffect, useCallback } from "react";

const API_URL = "/api";

const LAYER_COLORS = ["#e94560", "#0984e3", "#00b894", "#fdcb6e", "#a29bfe"];
const LAYER_LABELS = [
  "L1 Search Deflection",
  "L2 Zero-Click Impression",
  "L3 Competitive Displacement",
  "L4 AI Channel Loss",
  "L5 LTV Cascade",
];

const LAYER_DESCRIPTIONS = {
  l1_search_deflection:
    "Lost clicks from AI Overviews deflecting traffic away from organic results.",
  l2_zero_click_impression:
    "Lost brand impressions in zero-click searches where AI provides the answer.",
  l3_competitive_displacement:
    "Market share lost to competitors with higher AI visibility scores.",
  l4_ai_channel:
    "Missed referrals from ChatGPT, Perplexity, voice search, and other AI channels.",
  l5_ltv_cascade:
    "Lost repeat purchases from first-time customers deflected by AI results.",
};

const GROUPS = [
  {
    label: "Search & Discovery",
    color: "#0984e3",
    inputs: [
      {
        key: "monthly_search_volume",
        label: "Monthly Search Volume",
        min: 1000,
        max: 500000,
        step: 1000,
        fmt: (v) => v.toLocaleString(),
        tip: "Total monthly searches for your branded + category keywords",
      },
      {
        key: "ai_overview_capture_rate",
        label: "AI Overview Capture Rate",
        min: 0,
        max: 1,
        step: 0.01,
        fmt: (v) => `${(v * 100).toFixed(0)}%`,
        tip: "Fraction of searches where Google AI Overviews appear",
      },
      {
        key: "brand_mention_rate",
        label: "Brand Mention Rate",
        min: 0,
        max: 1,
        step: 0.01,
        fmt: (v) => `${(v * 100).toFixed(0)}%`,
        tip: "How often your brand appears in AI-generated answers",
      },
      {
        key: "competitor_mention_rate",
        label: "Competitor Mention Rate",
        min: 0,
        max: 1,
        step: 0.01,
        fmt: (v) => `${(v * 100).toFixed(0)}%`,
        tip: "How often competitors appear in AI answers for your keywords",
      },
    ],
  },
  {
    label: "Traffic Deflection",
    color: "#e94560",
    inputs: [
      {
        key: "organic_ctr",
        label: "Organic CTR",
        min: 0.001,
        max: 0.3,
        step: 0.001,
        fmt: (v) => `${(v * 100).toFixed(1)}%`,
        tip: "Current organic click-through rate from search results",
      },
      {
        key: "ctr_reduction",
        label: "CTR Reduction (AI)",
        min: 0,
        max: 1,
        step: 0.01,
        fmt: (v) => `${(v * 100).toFixed(0)}%`,
        tip: "Estimated CTR reduction caused by AI Overviews",
      },
      {
        key: "zero_click_rate",
        label: "Zero-Click Search Rate",
        min: 0,
        max: 1,
        step: 0.01,
        fmt: (v) => `${(v * 100).toFixed(0)}%`,
        tip: "Fraction of searches that end without any click",
      },
    ],
  },
  {
    label: "Revenue",
    color: "#00b894",
    inputs: [
      {
        key: "avg_order_value",
        label: "Average Order Value ($)",
        min: 1,
        max: 5000,
        step: 5,
        fmt: (v) => `$${v.toFixed(0)}`,
        tip: "Average revenue per transaction",
      },
      {
        key: "organic_conversion_rate",
        label: "Organic Conversion Rate",
        min: 0.001,
        max: 0.3,
        step: 0.001,
        fmt: (v) => `${(v * 100).toFixed(1)}%`,
        tip: "Percentage of organic visitors who convert",
      },
      {
        key: "customer_lifetime_value",
        label: "Customer Lifetime Value ($)",
        min: 1,
        max: 10000,
        step: 10,
        fmt: (v) => `$${v.toFixed(0)}`,
        tip: "Total revenue expected from a single customer",
      },
      {
        key: "repeat_purchase_rate",
        label: "Repeat Purchase Rate",
        min: 0,
        max: 1,
        step: 0.01,
        fmt: (v) => `${(v * 100).toFixed(0)}%`,
        tip: "Fraction of customers who make repeat purchases",
      },
    ],
  },
  {
    label: "Competitive",
    color: "#fdcb6e",
    inputs: [
      {
        key: "num_competitors_in_ai",
        label: "Competitors in AI Results",
        min: 0,
        max: 20,
        step: 1,
        fmt: (v) => Math.round(v).toString(),
        tip: "Number of competitors appearing in AI-generated answers",
      },
      {
        key: "market_share_at_risk",
        label: "Market Share at Risk",
        min: 0,
        max: 1,
        step: 0.01,
        fmt: (v) => `${(v * 100).toFixed(0)}%`,
        tip: "Percentage of your market share vulnerable to AI displacement",
      },
      {
        key: "competitor_ai_visibility",
        label: "Competitor AI Visibility",
        min: 0,
        max: 1,
        step: 0.01,
        fmt: (v) => `${(v * 100).toFixed(0)}%`,
        tip: "Average AI visibility score of your top competitors",
      },
    ],
  },
  {
    label: "AI Channels",
    color: "#a29bfe",
    inputs: [
      {
        key: "chatbot_referral_potential",
        label: "Chatbot Referral Potential",
        min: 0,
        max: 0.5,
        step: 0.005,
        fmt: (v) => `${(v * 100).toFixed(1)}%`,
        tip: "Fraction of searches where chatbots could refer your brand",
      },
      {
        key: "voice_search_share",
        label: "Voice Search Share",
        min: 0,
        max: 1,
        step: 0.01,
        fmt: (v) => `${(v * 100).toFixed(0)}%`,
        tip: "Fraction of total searches conducted via voice",
      },
      {
        key: "llm_citation_rate",
        label: "LLM Citation Rate",
        min: 0,
        max: 0.5,
        step: 0.005,
        fmt: (v) => `${(v * 100).toFixed(1)}%`,
        tip: "How often LLMs currently cite your brand",
      },
    ],
  },
];

const DEFAULTS = {
  monthly_search_volume: 50000,
  ai_overview_capture_rate: 0.35,
  brand_mention_rate: 0.1,
  competitor_mention_rate: 0.4,
  organic_ctr: 0.045,
  ctr_reduction: 0.3,
  zero_click_rate: 0.65,
  avg_order_value: 150,
  organic_conversion_rate: 0.025,
  customer_lifetime_value: 450,
  repeat_purchase_rate: 0.35,
  num_competitors_in_ai: 5,
  market_share_at_risk: 0.15,
  competitor_ai_visibility: 0.65,
  chatbot_referral_potential: 0.08,
  voice_search_share: 0.2,
  llm_citation_rate: 0.05,
};

function fmt$(v) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(2)}M`;
  if (v >= 1_000) return `$${(v / 1_000).toFixed(1)}K`;
  return `$${v.toFixed(2)}`;
}

function PieChart({ layers }) {
  const layerKeys = Object.keys(layers);
  const total = layerKeys.reduce((s, k) => s + layers[k], 0);
  if (total <= 0) return null;

  let cumAngle = -Math.PI / 2;
  const cx = 100,
    cy = 100,
    r = 80;

  const slices = layerKeys.map((k, i) => {
    const fraction = layers[k] / total;
    const angle = fraction * 2 * Math.PI;
    const x1 = cx + r * Math.cos(cumAngle);
    const y1 = cy + r * Math.sin(cumAngle);
    cumAngle += angle;
    const x2 = cx + r * Math.cos(cumAngle);
    const y2 = cy + r * Math.sin(cumAngle);
    const large = angle > Math.PI ? 1 : 0;
    return { key: k, color: LAYER_COLORS[i], x1, y1, x2, y2, large, fraction };
  });

  return (
    <div className="flex flex-col items-center gap-4">
      <svg viewBox="0 0 200 200" className="w-48 h-48">
        {slices.map((s) => (
          <path
            key={s.key}
            d={`M${cx},${cy} L${s.x1},${s.y1} A${r},${r} 0 ${s.large},1 ${s.x2},${s.y2} Z`}
            fill={s.color}
            stroke="#1a1a2e"
            strokeWidth="1.5"
          />
        ))}
      </svg>
      <div className="grid grid-cols-1 gap-1 w-full max-w-xs">
        {slices.map((s, i) => (
          <div key={s.key} className="flex items-center gap-2 text-xs">
            <span
              className="inline-block w-3 h-3 rounded-sm flex-shrink-0"
              style={{ background: s.color }}
            />
            <span className="text-gray-300 flex-1">{LAYER_LABELS[i]}</span>
            <span className="text-white font-medium">
              {(s.fraction * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function LostRevenue() {
  const [params, setParams] = useState(DEFAULTS);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState(false);
  const [methodologyOpen, setMethodologyOpen] = useState(false);
  const [activeTooltip, setActiveTooltip] = useState(null);

  const fetchCalc = useCallback(async (p) => {
    setLoading(true);
    try {
      const qs = new URLSearchParams(
        Object.entries(p).map(([k, v]) => [k, v])
      ).toString();
      const res = await fetch(`${API_URL}/lost-revenue/calculate?${qs}`);
      if (res.ok) {
        setResult(await res.json());
        setFetchError(false);
      } else {
        setFetchError(true);
      }
    } catch (_) {
      setFetchError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCalc(params);
  }, [params, fetchCalc]);

  function updateParam(key, value) {
    setParams((prev) => ({ ...prev, [key]: parseFloat(value) }));
  }

  return (
    <div className="min-h-screen bg-[#1a1a2e] text-white font-sans">
      {/* Header */}
      <header className="border-b border-[#0f3460] px-6 py-4 flex items-center justify-between">
        <a href="/" className="text-sm text-[#0984e3] hover:underline">
          ← GEO Score
        </a>
        <h1 className="text-lg font-bold text-white">
          AI Invisibility Lost Revenue Calculator
        </h1>
        <span className="text-xs text-gray-400">5-Layer Attribution Model</span>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left: Input panels */}
        <div className="xl:col-span-2 space-y-6">
          {GROUPS.map((group) => (
            <div
              key={group.label}
              className="bg-[#16213e] rounded-xl p-5 border border-[#0f3460]"
            >
              <h2
                className="text-sm font-bold uppercase tracking-wider mb-4"
                style={{ color: group.color }}
              >
                {group.label}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                {group.inputs.map((inp) => (
                  <div key={inp.key} className="space-y-1">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1">
                        <label className="text-xs text-gray-300 font-medium">
                          {inp.label}
                        </label>
                        <button
                          className="text-gray-500 hover:text-gray-300 text-xs leading-none"
                          onMouseEnter={() => setActiveTooltip(inp.key)}
                          onMouseLeave={() => setActiveTooltip(null)}
                          aria-label="More info"
                        >
                          ⓘ
                        </button>
                      </div>
                      <span
                        className="text-xs font-bold"
                        style={{ color: group.color }}
                      >
                        {inp.fmt(params[inp.key])}
                      </span>
                    </div>
                    {activeTooltip === inp.key && (
                      <p className="text-xs text-gray-400 bg-[#0f3460] rounded px-2 py-1">
                        {inp.tip}
                      </p>
                    )}
                    <input
                      type="range"
                      min={inp.min}
                      max={inp.max}
                      step={inp.step}
                      value={params[inp.key]}
                      onChange={(e) => updateParam(inp.key, e.target.value)}
                      className="w-full h-1.5 rounded-full appearance-none bg-[#0f3460] accent-current cursor-pointer"
                      style={{ accentColor: group.color }}
                    />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Right: Results */}
        <div className="space-y-6">
          {/* KPI Cards */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#16213e] rounded-xl p-4 border border-[#e94560]/30">
              <p className="text-xs text-gray-400 mb-1">Monthly Loss</p>
              <p className="text-2xl font-bold text-[#e94560]">
                {result ? fmt$(result.monthly_lost_revenue) : "—"}
              </p>
            </div>
            <div className="bg-[#16213e] rounded-xl p-4 border border-[#e94560]/30">
              <p className="text-xs text-gray-400 mb-1">Annual Loss</p>
              <p className="text-2xl font-bold text-[#e94560]">
                {result ? fmt$(result.annual_lost_revenue) : "—"}
              </p>
            </div>
            <div className="bg-[#16213e] rounded-xl p-4 border border-[#0984e3]/30">
              <p className="text-xs text-gray-400 mb-1">Lost Customers/mo</p>
              <p className="text-2xl font-bold text-[#0984e3]">
                {result
                  ? Math.round(result.lost_customers_monthly).toLocaleString()
                  : "—"}
              </p>
            </div>
            <div className="bg-[#16213e] rounded-xl p-4 border border-[#fdcb6e]/30">
              <p className="text-xs text-gray-400 mb-1">Market Share at Risk</p>
              <p className="text-2xl font-bold text-[#fdcb6e]">
                {result ? `${result.market_share_at_risk_pct}%` : "—"}
              </p>
            </div>
          </div>

          {/* Confidence */}
          {result && (
            <div className="bg-[#16213e] rounded-xl p-4 border border-[#0f3460]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-400">Model Confidence</span>
                <span className="text-xs font-bold text-[#00b894]">
                  {(result.model_confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-[#0f3460] rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-[#00b894] transition-all duration-300"
                  style={{ width: `${result.model_confidence * 100}%` }}
                />
              </div>
            </div>
          )}

          {/* Pie Chart */}
          {result && result.layers && (
            <div className="bg-[#16213e] rounded-xl p-5 border border-[#0f3460]">
              <h3 className="text-sm font-bold text-gray-300 mb-4">
                5-Layer Breakdown
              </h3>
              <PieChart layers={result.layers} />
            </div>
          )}

          {/* Layer detail cards */}
          {result && result.layers && (
            <div className="bg-[#16213e] rounded-xl p-5 border border-[#0f3460] space-y-3">
              <h3 className="text-sm font-bold text-gray-300">
                Attribution Detail
              </h3>
              {Object.entries(result.layers).map(([key, val], i) => (
                <div key={key}>
                  <div className="flex items-center justify-between">
                    <span
                      className="text-xs font-medium"
                      style={{ color: LAYER_COLORS[i] }}
                    >
                      {LAYER_LABELS[i]}
                    </span>
                    <span className="text-xs text-white font-bold">
                      {fmt$(val)}/mo
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {LAYER_DESCRIPTIONS[key]}
                  </p>
                  {key === "l4_ai_channel" && result.l4_breakdown && (
                    <div className="ml-3 mt-1 space-y-0.5">
                      <div className="flex justify-between text-xs text-gray-400">
                        <span>↳ Chatbot</span>
                        <span>{fmt$(result.l4_breakdown.chatbot)}</span>
                      </div>
                      <div className="flex justify-between text-xs text-gray-400">
                        <span>↳ Voice</span>
                        <span>{fmt$(result.l4_breakdown.voice)}</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Loading indicator */}
          {loading && (
            <p className="text-xs text-gray-500 text-center">Calculating…</p>
          )}

          {/* Error indicator */}
          {fetchError && !loading && (
            <p className="text-xs text-[#e94560] text-center bg-[#16213e] rounded px-3 py-2 border border-[#e94560]/30">
              ⚠ Could not reach the calculation API. Showing last known results.
            </p>
          )}

          {/* Methodology toggle */}
          <div className="bg-[#16213e] rounded-xl border border-[#0f3460] overflow-hidden">
            <button
              className="w-full px-5 py-3 flex items-center justify-between text-sm text-gray-300 hover:text-white"
              onClick={() => setMethodologyOpen((o) => !o)}
            >
              <span className="font-medium">Methodology</span>
              <span>{methodologyOpen ? "▲" : "▼"}</span>
            </button>
            {methodologyOpen && (
              <div className="px-5 pb-5 text-xs text-gray-400 space-y-3 border-t border-[#0f3460]">
                <p className="pt-3">
                  This calculator uses a <strong className="text-gray-200">5-layer attribution model</strong>{" "}
                  to estimate monthly and annual revenue loss from AI search
                  invisibility.
                </p>
                <div>
                  <p className="text-gray-200 font-semibold">
                    L1 – Search Deflection
                  </p>
                  <p>
                    Searches × AI_Capture% × (1 − Brand_Mention%) ×
                    Organic_CTR% × CTR_Reduction%
                  </p>
                </div>
                <div>
                  <p className="text-gray-200 font-semibold">
                    L2 – Zero-Click Impression Loss
                  </p>
                  <p>
                    Impression_Value × Zero_Click% × AI_Capture% × (1 −
                    Brand_Mention%)
                  </p>
                </div>
                <div>
                  <p className="text-gray-200 font-semibold">
                    L3 – Competitive Displacement
                  </p>
                  <p>
                    Monthly_Organic_Revenue × Market_Share_At_Risk% ×
                    Visibility_Gap
                  </p>
                </div>
                <div>
                  <p className="text-gray-200 font-semibold">
                    L4 – AI Channel Loss
                  </p>
                  <p>Chatbot losses + Voice search losses</p>
                </div>
                <div>
                  <p className="text-gray-200 font-semibold">
                    L5 – Lifetime Value Cascade
                  </p>
                  <p>
                    Lost_Customers × (CLV − AOV) × Repeat_Rate%
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
