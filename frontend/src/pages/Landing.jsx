import { useState } from "react";

const FEATURES = [
  {
    title: "AI Citability Score",
    desc: "How likely ChatGPT, Claude, and Perplexity are to cite your content",
  },
  {
    title: "Brand Authority Map",
    desc: "Your presence on YouTube, Reddit, Wikipedia, and LinkedIn",
  },
  {
    title: "AI Crawler Access",
    desc: "Which AI bots can see your site (GPTBot, ClaudeBot, PerplexityBot)",
  },
  {
    title: "Technical GEO Audit",
    desc: "Server-side rendering, Core Web Vitals, security headers",
  },
  {
    title: "Schema & Structured Data",
    desc: "JSON-LD markup validation and missing schema opportunities",
  },
  {
    title: "30-Day Action Plan",
    desc: "Prioritized quick wins, medium-term fixes, and strategic moves",
  },
];

export default function Landing({ apiUrl }) {
  const [url, setUrl] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${apiUrl}/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, email }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Something went wrong");
        setLoading(false);
        return;
      }

      // Redirect to Stripe Checkout
      window.location.href = data.checkout_url;
    } catch (err) {
      setError("Network error. Please try again.");
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-navy">
      {/* Hero */}
      <div className="max-w-4xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="inline-block bg-accent/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
          AI search is eating traditional search
        </div>

        <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight mb-6">
          How Does AI
          <br />
          <span className="text-coral">See Your Website?</span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-12">
          Get a comprehensive GEO (Generative Engine Optimization) audit.
          See exactly how ChatGPT, Perplexity, Gemini, and Google AI Overviews
          discover, understand, and cite your content.
        </p>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="max-w-xl mx-auto bg-navy-light border border-gray-700 rounded-2xl p-8 shadow-2xl"
        >
          <div className="mb-4">
            <input
              type="text"
              placeholder="Enter your website URL"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              className="w-full px-4 py-3 bg-navy border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-coral focus:ring-1 focus:ring-coral text-lg"
            />
          </div>

          <div className="mb-6">
            <input
              type="email"
              placeholder="Your email (to receive the report)"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 bg-navy border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-coral focus:ring-1 focus:ring-coral text-lg"
            />
          </div>

          {error && (
            <div className="mb-4 text-red-400 text-sm">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-coral hover:bg-red-500 disabled:opacity-50 text-white font-bold text-lg rounded-lg transition-colors"
          >
            {loading ? "Redirecting to checkout..." : "Get My GEO Report — $49"}
          </button>

          <p className="text-gray-500 text-sm mt-3">
            One-time payment. Report delivered in ~10 minutes. No subscription.
          </p>
        </form>
      </div>

      {/* What's Included */}
      <div className="max-w-5xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center text-white mb-12">
          What's in Your GEO Report
        </h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="bg-navy-light border border-gray-700 rounded-xl p-6 hover:border-accent transition-colors"
            >
              <h3 className="text-lg font-semibold text-white mb-2">
                {f.title}
              </h3>
              <p className="text-gray-400 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Bar */}
      <div className="border-t border-gray-800 bg-navy-light">
        <div className="max-w-5xl mx-auto px-6 py-12 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-coral">+527%</div>
            <div className="text-gray-500 text-sm mt-1">AI traffic growth (2025)</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-coral">1.5B</div>
            <div className="text-gray-500 text-sm mt-1">Google AI Overview users/mo</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-coral">900M+</div>
            <div className="text-gray-500 text-sm mt-1">ChatGPT weekly users</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-coral">-50%</div>
            <div className="text-gray-500 text-sm mt-1">Predicted search drop by 2028</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center text-gray-600 text-sm py-8">
        GEO Score &mdash; AI Search Visibility Analysis
      </footer>
    </div>
  );
}
