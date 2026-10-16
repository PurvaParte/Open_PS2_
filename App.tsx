
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import StudentDashboard from "./pages/StudentDashboard";
import CodingAssessment from "./pages/CodingAssessment";
import CodeViva from "./pages/CodeViva";
import ReplayReview from "./pages/ReplayReview";
import TrainerDashboard from "./pages/TrainerDashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/student" replace />} />
        <Route path="/student" element={<StudentDashboard />} />
        <Route path="/assessment" element={<CodingAssessment />} />
        <Route path="/viva" element={<CodeViva />} />
        <Route path="/replay" element={<ReplayReview />} />
        <Route path="/trainer" element={<TrainerDashboard />} />
        <Route path="*" element={<Navigate to="/student" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
