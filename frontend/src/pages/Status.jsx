import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

const PROGRESS_STEPS = [
  "Queued for processing",
  "Starting GEO audit",
  "Fetching and analyzing website",
  "Scoring AI citability",
  "Scanning brand authority signals",
  "Checking llms.txt and AI crawler access",
  "Computing GEO scores",
  "Generating professional PDF report",
  "Report complete!",
];

function getStepIndex(message) {
  if (!message) return 0;
  const msg = message.toLowerCase();
  for (let i = PROGRESS_STEPS.length - 1; i >= 0; i--) {
    if (msg.includes(PROGRESS_STEPS[i].toLowerCase().slice(0, 15))) return i;
  }
  if (msg.includes("fetching")) return 2;
  if (msg.includes("citab")) return 3;
  if (msg.includes("brand")) return 4;
  if (msg.includes("llms") || msg.includes("crawler")) return 5;
  if (msg.includes("scor")) return 6;
  if (msg.includes("pdf") || msg.includes("generat")) return 7;
  if (msg.includes("complete") || msg.includes("ready")) return 8;
  return 1;
}

function ScoreGauge({ score }) {
  const color =
    score >= 80
      ? "#00b894"
      : score >= 60
        ? "#0f3460"
        : score >= 40
          ? "#fdcb6e"
          : "#d63031";

  return (
    <div className="flex flex-col items-center">
      <div
        className="w-32 h-32 rounded-full border-8 flex items-center justify-center"
        style={{ borderColor: color }}
      >
        <span className="text-4xl font-extrabold text-white">{score}</span>
      </div>
      <span className="text-gray-400 mt-2">out of 100</span>
    </div>
  );
}

export default function Status({ apiUrl }) {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let interval;

    async function poll() {
      try {
        const res = await fetch(`${apiUrl}/status/${jobId}`);
        if (!res.ok) {
          setError("Report not found");
          return;
        }
        const data = await res.json();
        setJob(data);

        if (data.status === "completed" || data.status === "failed") {
          clearInterval(interval);
        }
      } catch {
        // Silently retry on network error
      }
    }

    poll();
    interval = setInterval(poll, 5000);

    return () => clearInterval(interval);
  }, [jobId, apiUrl]);

  const stepIndex = getStepIndex(job?.progress_message);
  const progress = Math.min(100, Math.round((stepIndex / (PROGRESS_STEPS.length - 1)) * 100));

  return (
    <div className="min-h-screen bg-navy flex items-center justify-center px-6">
      <div className="max-w-lg w-full text-center">
        {error ? (
          <div>
            <h1 className="text-3xl font-bold text-white mb-4">Report Not Found</h1>
            <p className="text-gray-400">
              This link may be invalid or expired.
            </p>
          </div>
        ) : !job ? (
          <div className="animate-pulse-slow">
            <h1 className="text-2xl font-bold text-white">Loading...</h1>
          </div>
        ) : job.status === "completed" ? (
          <div>
            <h1 className="text-3xl font-bold text-white mb-6">
              Your GEO Report is Ready!
            </h1>

            <div className="mb-8">
              <ScoreGauge score={job.geo_score} />
            </div>

            <p className="text-gray-400 mb-2">{job.url}</p>

            <a
              href={job.download_url}
              className="inline-block mt-6 px-8 py-4 bg-coral hover:bg-red-500 text-white font-bold text-lg rounded-lg transition-colors"
            >
              Download PDF Report
            </a>

            <p className="text-gray-500 text-sm mt-4">
              A copy has also been sent to your email.
            </p>
          </div>
        ) : job.status === "failed" ? (
          <div>
            <h1 className="text-3xl font-bold text-white mb-4">
              Something Went Wrong
            </h1>
            <p className="text-gray-400 mb-4">
              {job.error_message || "We encountered an issue generating your report."}
            </p>
            <p className="text-gray-500 text-sm">
              Our team has been notified. We'll email your report once resolved.
            </p>
          </div>
        ) : (
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Analyzing Your Website
            </h1>
            <p className="text-gray-400 mb-8">{job.url}</p>

            {/* Progress bar */}
            <div className="w-full bg-gray-800 rounded-full h-3 mb-4">
              <div
                className="bg-coral h-3 rounded-full transition-all duration-1000"
                style={{ width: `${progress}%` }}
              />
            </div>

            <p className="text-gray-300 font-medium mb-2">
              {job.progress_message || "Starting..."}
            </p>
            <p className="text-gray-500 text-sm">
              This usually takes 5-10 minutes. You can leave this page open.
            </p>

            {/* Step list */}
            <div className="mt-8 text-left max-w-xs mx-auto">
              {PROGRESS_STEPS.slice(2, -1).map((step, i) => {
                const actualIndex = i + 2;
                const done = stepIndex > actualIndex;
                const active = stepIndex === actualIndex;
                return (
                  <div
                    key={step}
                    className={`flex items-center gap-3 py-2 text-sm ${
                      done
                        ? "text-success"
                        : active
                          ? "text-white font-medium"
                          : "text-gray-600"
                    }`}
                  >
                    <span className="w-5 text-center">
                      {done ? "\u2713" : active ? "\u25CF" : "\u25CB"}
                    </span>
                    {step}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
