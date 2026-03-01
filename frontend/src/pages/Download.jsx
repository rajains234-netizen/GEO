import { useParams } from "react-router-dom";

export default function Download({ apiUrl }) {
  const { jobId, token } = useParams();
  const downloadUrl = `${apiUrl}/download/${jobId}/${token}`;

  return (
    <div className="min-h-screen bg-navy flex items-center justify-center px-6">
      <div className="max-w-lg w-full text-center">
        <h1 className="text-3xl font-bold text-white mb-6">
          Download Your GEO Report
        </h1>

        <a
          href={downloadUrl}
          className="inline-block px-8 py-4 bg-coral hover:bg-red-500 text-white font-bold text-lg rounded-lg transition-colors"
        >
          Download PDF Report
        </a>

        <p className="text-gray-500 text-sm mt-6">
          If the download doesn't start,{" "}
          <a href={downloadUrl} className="text-coral underline">
            click here
          </a>
          .
        </p>
      </div>
    </div>
  );
}
