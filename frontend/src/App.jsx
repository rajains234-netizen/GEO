import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Status from "./pages/Status";
import Download from "./pages/Download";
import LostRevenue from "./pages/LostRevenue";

const API_URL = "/api";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing apiUrl={API_URL} />} />
        <Route path="/status/:jobId" element={<Status apiUrl={API_URL} />} />
        <Route
          path="/download/:jobId/:token"
          element={<Download apiUrl={API_URL} />}
        />
        <Route path="/lost-revenue" element={<LostRevenue />} />
      </Routes>
    </BrowserRouter>
  );
}
