import React from "react";
import { useNavigate } from "react-router-dom";
import TerminalShell from "@/components/TerminalShell";
import { useAuth } from "@/context/AuthContext";

const MenuItem = ({ label, description, onClick, testId, accent = "green" }) => {
  const colorMap = {
    green: "border-green-700 text-green-400 hover:bg-green-500 hover:text-black hover:border-green-500",
    yellow: "border-yellow-700 text-yellow-400 hover:bg-yellow-400 hover:text-black hover:border-yellow-400",
    red: "border-red-800 text-red-400 hover:bg-red-500 hover:text-black hover:border-red-500",
  };
  return (
    <button
      onClick={onClick}
      data-testid={testId}
      className={`w-full text-left border ${colorMap[accent]} bg-black/60 p-6 font-mono transition-none group`}
    >
      <div className="flex items-baseline justify-between">
        <span className="text-xl md:text-2xl uppercase tracking-widest text-glow">&gt; {label}</span>
        <span className="opacity-0 group-hover:opacity-100 text-sm">[ENTER]</span>
      </div>
      <div className="text-xs md:text-sm opacity-70 mt-2 uppercase tracking-wide">{description}</div>
    </button>
  );
};

export default function Home() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  return (
    <TerminalShell>
      <div className="fade-in">
        <div className="mb-10">
          <div className="text-green-700 text-xs mb-2 font-mono uppercase tracking-widest">
            [session initialized]
          </div>
          <h1 className="text-4xl md:text-6xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow-strong" data-testid="welcome-heading">
            WELCOME, <span className="text-yellow-400">{user?.name}</span>
            <span className="cursor-blink"></span>
          </h1>
          <p className="mt-4 text-green-600 font-mono max-w-xl">
            <span className="text-green-800">$</span> Select an operation from the main menu below. Your progress and scores are recorded to the central server.
          </p>
        </div>

        <div className="mb-4 text-green-700 text-xs font-mono uppercase tracking-widest">
          ┌─── MAIN MENU ───────────────────────────────
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="main-menu">
          <MenuItem
            label="Start Quiz"
            description="Choose category & difficulty · timed questions"
            onClick={() => navigate("/setup")}
            testId="menu-start-quiz"
          />
          <MenuItem
            label="Leaderboard"
            description="Top scores across all players"
            onClick={() => navigate("/leaderboard")}
            testId="menu-leaderboard"
            accent="yellow"
          />
          <MenuItem
            label="My Stats"
            description="Personal performance & history"
            onClick={() => navigate("/stats")}
            testId="menu-stats"
          />
          <MenuItem
            label="Exit / Logout"
            description="Terminate session"
            onClick={async () => { await logout(); navigate("/login"); }}
            testId="menu-exit"
            accent="red"
          />
        </div>

        <div className="mt-2 text-green-700 text-xs font-mono uppercase tracking-widest">
          └────────────────────────────────────────────
        </div>
      </div>
    </TerminalShell>
  );
}
