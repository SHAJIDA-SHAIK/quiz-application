import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

export const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (user === null) {
    return (
      <div className="flex items-center justify-center min-h-screen text-green-500 font-mono text-glow" data-testid="auth-loading">
        <span className="cursor-blink">INITIALIZING SESSION</span>
      </div>
    );
  }
  if (user === false) return <Navigate to="/login" replace />;
  return children;
};

export default ProtectedRoute;
