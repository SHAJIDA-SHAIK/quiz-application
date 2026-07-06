import React, { useEffect, useState } from "react";
import TerminalShell from "@/components/TerminalShell";
import { api } from "@/lib/api";

const CATEGORY_FILTERS = ["All", "Python", "DBMS", "OS", "Aptitude"];

export default function Leaderboard() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    let cancel = false;
    (async () => {
      setLoading(true);
      const params = { limit: 10 };
      if (filter !== "All") params.category = filter;
      try {
        const { data } = await api.get("/quiz/leaderboard", { params });
        if (!cancel) setEntries(data);
      } finally {
        if (!cancel) setLoading(false);
      }
    })();
    return () => { cancel = true; };
  }, [filter]);

  return (
    <TerminalShell>
      <div className="fade-in max-w-5xl">
        <div className="text-green-700 text-xs uppercase tracking-widest mb-2 font-mono">[global_ranking]</div>
        <h1 className="text-3xl md:text-5xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow-strong mb-2">
          === LEADERBOARD ===
        </h1>
        <p className="text-green-600 font-mono mb-8">
          <span className="text-green-800">$</span> top scores across the network<span className="cursor-blink"></span>
        </p>

        <div className="flex flex-wrap gap-2 mb-6" data-testid="leaderboard-filters">
          {CATEGORY_FILTERS.map((c) => (
            <button
              key={c}
              onClick={() => setFilter(c)}
              data-testid={`filter-${c.toLowerCase()}`}
              className={`px-3 py-1 border font-mono uppercase tracking-widest text-xs ${
                filter === c ? "bg-green-500 text-black border-green-500" : "text-green-400 border-green-800 hover:border-green-500"
              }`}
            >
              {c}
            </button>
          ))}
        </div>

        <div className="terminal-frame p-4 md:p-6 pt-10 md:pt-12 overflow-x-auto">
          {loading ? (
            <div className="text-green-500 font-mono cursor-blink" data-testid="leaderboard-loading">FETCHING DATA</div>
          ) : entries.length === 0 ? (
            <div className="text-green-600 font-mono" data-testid="leaderboard-empty">
              &gt; no scores yet. be the first to log an entry.
            </div>
          ) : (
            <table className="w-full font-mono text-sm md:text-base" data-testid="leaderboard-table">
              <thead>
                <tr className="text-green-700 uppercase tracking-widest text-xs">
                  <th className="text-left py-2 px-2">Rank</th>
                  <th className="text-left py-2 px-2">Player</th>
                  <th className="text-left py-2 px-2 hidden md:table-cell">Category</th>
                  <th className="text-left py-2 px-2 hidden md:table-cell">Difficulty</th>
                  <th className="text-right py-2 px-2">Accuracy</th>
                  <th className="text-right py-2 px-2">Score</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((e) => {
                  const medal = e.rank === 1 ? "text-yellow-400 text-glow-yellow" : e.rank === 2 ? "text-green-300" : e.rank === 3 ? "text-green-500" : "text-green-600";
                  return (
                    <tr key={`${e.rank}-${e.user_name}-${e.created_at}`} className="border-t border-green-900" data-testid={`leaderboard-row-${e.rank}`}>
                      <td className={`py-3 px-2 font-bold ${medal}`}>#{String(e.rank).padStart(2, "0")}</td>
                      <td className="py-3 px-2 text-green-300">{e.user_name}</td>
                      <td className="py-3 px-2 text-green-600 hidden md:table-cell">{e.category}</td>
                      <td className="py-3 px-2 text-green-600 hidden md:table-cell">{e.difficulty}</td>
                      <td className="py-3 px-2 text-right text-green-400">{e.accuracy}%</td>
                      <td className={`py-3 px-2 text-right font-bold ${medal}`}>{e.score}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </TerminalShell>
  );
}
