import React, { useEffect, useState } from "react";
import TerminalShell from "@/components/TerminalShell";
import { api } from "@/lib/api";

export default function Stats() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    (async () => {
      const { data } = await api.get("/quiz/stats");
      setStats(data);
    })();
  }, []);

  if (!stats) {
    return (
      <TerminalShell>
        <div className="text-green-500 font-mono cursor-blink" data-testid="stats-loading">LOADING TELEMETRY</div>
      </TerminalShell>
    );
  }

  const bar = (v) => {
    const filled = Math.round((v / 100) * 20);
    return "#".repeat(filled) + "-".repeat(20 - filled);
  };

  return (
    <TerminalShell>
      <div className="fade-in max-w-5xl">
        <div className="text-green-700 text-xs uppercase tracking-widest mb-2 font-mono">[performance_log]</div>
        <h1 className="text-3xl md:text-5xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow-strong mb-8">
          === MY STATS ===
        </h1>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10" data-testid="stats-summary">
          <div className="border border-green-800 bg-black/60 p-5">
            <div className="text-xs uppercase text-green-700 font-mono">Games</div>
            <div className="text-3xl md:text-4xl font-bold font-mono mt-1 text-green-400 text-glow" data-testid="stat-games">{stats.games_played}</div>
          </div>
          <div className="border border-green-800 bg-black/60 p-5">
            <div className="text-xs uppercase text-green-700 font-mono">Best Score</div>
            <div className="text-3xl md:text-4xl font-bold font-mono mt-1 text-yellow-400 text-glow-yellow" data-testid="stat-best">{stats.best_score}</div>
          </div>
          <div className="border border-green-800 bg-black/60 p-5">
            <div className="text-xs uppercase text-green-700 font-mono">Avg Accuracy</div>
            <div className="text-3xl md:text-4xl font-bold font-mono mt-1 text-green-400 text-glow" data-testid="stat-accuracy">{stats.avg_accuracy}%</div>
          </div>
          <div className="border border-green-800 bg-black/60 p-5">
            <div className="text-xs uppercase text-green-700 font-mono">Total Correct</div>
            <div className="text-3xl md:text-4xl font-bold font-mono mt-1 text-green-400 text-glow" data-testid="stat-correct">{stats.total_correct}/{stats.total_questions}</div>
          </div>
        </div>

        <h2 className="text-xl font-mono uppercase tracking-widest text-green-500 text-glow mb-4">&gt; per-category breakdown</h2>
        <div className="terminal-frame p-4 md:p-6 pt-10 mb-10">
          {Object.keys(stats.by_category).length === 0 ? (
            <div className="text-green-600 font-mono" data-testid="stats-empty">&gt; no games played yet.</div>
          ) : (
            <div className="space-y-3 font-mono">
              {Object.entries(stats.by_category).map(([cat, e]) => (
                <div key={cat} className="border-b border-green-900 pb-3 last:border-0" data-testid={`cat-row-${cat.toLowerCase()}`}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-green-300 uppercase tracking-widest">{cat}</span>
                    <span className="text-green-500">{e.accuracy}%  ·  best: <span className="text-yellow-400">{e.best_score}</span>  ·  games: {e.games}</span>
                  </div>
                  <div className="text-green-500 text-xs">[{bar(e.accuracy)}]</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <h2 className="text-xl font-mono uppercase tracking-widest text-green-500 text-glow mb-4">&gt; recent sessions</h2>
        <div className="terminal-frame p-4 md:p-6 pt-10 overflow-x-auto">
          {stats.recent.length === 0 ? (
            <div className="text-green-600 font-mono">&gt; empty log.</div>
          ) : (
            <table className="w-full font-mono text-sm" data-testid="recent-table">
              <thead>
                <tr className="text-green-700 uppercase tracking-widest text-xs">
                  <th className="text-left py-2 px-2">When</th>
                  <th className="text-left py-2 px-2">Category</th>
                  <th className="text-left py-2 px-2">Difficulty</th>
                  <th className="text-right py-2 px-2">Accuracy</th>
                  <th className="text-right py-2 px-2">Score</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent.map((r, i) => (
                  <tr key={i} className="border-t border-green-900">
                    <td className="py-2 px-2 text-green-600">{new Date(r.created_at).toLocaleString()}</td>
                    <td className="py-2 px-2 text-green-400">{r.category}</td>
                    <td className="py-2 px-2 text-green-400">{r.difficulty}</td>
                    <td className="py-2 px-2 text-right text-green-400">{r.accuracy}%</td>
                    <td className="py-2 px-2 text-right text-yellow-400 font-bold">{r.score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </TerminalShell>
  );
}
