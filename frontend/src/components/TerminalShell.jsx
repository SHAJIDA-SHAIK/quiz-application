import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

export const TerminalShell = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const navLink = (path, label, testId) => {
    const active = location.pathname === path;
    return (
      <button
        onClick={() => navigate(path)}
        data-testid={testId}
        className={`px-3 py-1 border border-green-800 hover:bg-green-500 hover:text-black transition-none text-glow font-mono text-sm uppercase tracking-wider ${
          active ? "bg-green-500/20 border-green-500" : ""
        }`}
      >
        {label}
      </button>
    );
  };

  return (
    <div className="min-h-screen relative z-10">
      {/* Top bar */}
      <header className="border-b border-green-900 bg-black/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-4 md:px-8 py-3">
          <button
            onClick={() => navigate("/")}
            data-testid="brand-home"
            className="font-mono font-bold text-green-500 text-glow uppercase tracking-widest text-sm md:text-base"
          >
            <span className="text-green-700">$</span> ./retro_quiz.exe
          </button>
          <nav className="flex items-center gap-2">
            {user && (
              <>
                {navLink("/", "Menu", "nav-menu")}
                {navLink("/leaderboard", "Leaderboard", "nav-leaderboard")}
                {navLink("/stats", "Stats", "nav-stats")}
                <span className="hidden md:inline text-green-700 mx-1">|</span>
                <span className="hidden md:inline text-green-600 text-xs uppercase" data-testid="current-user-name">
                  user: <span className="text-green-400">{user.name}</span>
                </span>
                <button
                  onClick={async () => { await logout(); navigate("/login"); }}
                  data-testid="logout-button"
                  className="px-3 py-1 border border-red-700 text-red-400 hover:bg-red-500 hover:text-black text-sm uppercase tracking-wider"
                >
                  Logout
                </button>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 md:px-8 py-8 md:py-12 crt-flicker">
        {children}
      </main>

      <footer className="border-t border-green-900 mt-16 py-4 text-center text-green-800 text-xs font-mono">
        &lt;/&gt; RETRO QUIZ v1.0 &mdash; SYSTEM READY
      </footer>
    </div>
  );
};

export default TerminalShell;
