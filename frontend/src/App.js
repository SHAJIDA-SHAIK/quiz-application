import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import ScanlineOverlay from "@/components/ScanlineOverlay";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Home from "@/pages/Home";
import Setup from "@/pages/Setup";
import Quiz from "@/pages/Quiz";
import Results from "@/pages/Results";
import Leaderboard from "@/pages/Leaderboard";
import Stats from "@/pages/Stats";

function App() {
  return (
    <div className="app-shell">
      <ScanlineOverlay />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/setup" element={<ProtectedRoute><Setup /></ProtectedRoute>} />
            <Route path="/quiz" element={<ProtectedRoute><Quiz /></ProtectedRoute>} />
            <Route path="/results" element={<ProtectedRoute><Results /></ProtectedRoute>} />
            <Route path="/leaderboard" element={<ProtectedRoute><Leaderboard /></ProtectedRoute>} />
            <Route path="/stats" element={<ProtectedRoute><Stats /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
