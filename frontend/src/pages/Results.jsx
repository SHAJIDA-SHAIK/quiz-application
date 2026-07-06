import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import TerminalShell from "@/components/TerminalShell";

const Stat = ({ label, value, accent = "green", testId }) => {
  const colors = {
    green: "text-green-400 text-glow",
    yellow: "text-yellow-400 text-glow-yellow",
    red: "text-red-400 text-glow-red",
  };
  return (
    <div className="border border-green-800 bg-black/60 p-5" data-testid={testId}>
      <div className="text-xs uppercase tracking-widest text-green-700 font-mono">{label}</div>
      <div className={`text-3xl md:text-4xl font-bold font-mono mt-1 ${colors[accent]}`}>{value}</div>
    </div>
  );
};

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;
  const category = location.state?.category;
  const difficulty = location.state?.difficulty;

  if (!result) {
    return (
      <TerminalShell>
        <div className="text-green-500 font-mono">
          <p>No result data. <button onClick={() => navigate("/")} className="text-yellow-400 underline">Go home</button></p>
        </div>
      </TerminalShell>
    );
  }

  const accent = result.accuracy >= 80 ? "green" : result.accuracy >= 50 ? "yellow" : "red";

  return (
    <TerminalShell>
      <div className="fade-in max-w-4xl" data-testid="results-screen">
        <div className="text-green-700 text-xs uppercase tracking-widest mb-2 font-mono">[quiz_complete]</div>
        <h1 className="text-3xl md:text-5xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow-strong mb-8">
          === RESULTS ===
        </h1>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          <Stat label="Total Score" value={result.score} accent="yellow" testId="result-score" />
          <Stat label="Correct" value={result.correct} accent="green" testId="result-correct" />
          <Stat label="Wrong" value={result.wrong} accent="red" testId="result-wrong" />
          <Stat label="Accuracy" value={`${result.accuracy}%`} accent={accent} testId="result-accuracy" />
        </div>

        <div className="mb-8 border border-green-800 bg-black/60 p-4 font-mono text-green-500">
          <span className="text-green-700">$</span> Category: <span className="text-yellow-400">{category}</span>
          <span className="mx-2 text-green-800">|</span>
          Difficulty: <span className="text-yellow-400">{difficulty}</span>
          <span className="mx-2 text-green-800">|</span>
          Questions: <span className="text-yellow-400">{result.total}</span>
        </div>

        <h2 className="text-xl font-mono uppercase tracking-widest text-green-500 text-glow mb-4">
          &gt; ANSWER REVIEW
        </h2>

        <div className="space-y-4 mb-10" data-testid="review-list">
          {result.review.map((r, i) => (
            <div key={r.question_id} className={`border p-4 md:p-5 bg-black/60 ${r.is_correct ? "border-green-700" : "border-red-800"}`} data-testid={`review-item-${i}`}>
              <div className="text-green-700 font-mono text-xs uppercase tracking-widest mb-2">
                Q{i + 1} &mdash; {r.is_correct ? <span className="text-green-400 text-glow">✓ correct</span> : <span className="text-red-400 text-glow-red">✗ incorrect</span>}
              </div>
              <div className="text-green-300 font-mono mb-3">{r.question}</div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {r.options.map((opt, oi) => {
                  const isCorrect = oi === r.correct_index;
                  const isSelected = oi === r.selected_index;
                  let cls = "border-green-900 text-green-600";
                  if (isCorrect) cls = "border-green-500 text-green-300 bg-green-950/40 text-glow";
                  else if (isSelected) cls = "border-red-500 text-red-300 bg-red-950/40 text-glow-red";
                  return (
                    <div key={oi} className={`border px-3 py-2 font-mono text-sm ${cls}`}>
                      <span className="mr-2 opacity-70">[{String.fromCharCode(65 + oi)}]</span>
                      {opt}
                      {isCorrect && <span className="ml-2 text-xs">← correct</span>}
                      {isSelected && !isCorrect && <span className="ml-2 text-xs">← your answer</span>}
                    </div>
                  );
                })}
                {r.selected_index === null && (
                  <div className="text-yellow-400 text-xs font-mono italic">! no answer submitted (timeout)</div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => navigate("/setup")}
            data-testid="play-again-button"
            className="px-6 py-3 border border-green-500 bg-black text-green-400 hover:bg-green-500 hover:text-black font-mono uppercase tracking-widest text-glow"
          >
            [ ▶ PLAY AGAIN ]
          </button>
          <button
            onClick={() => navigate("/leaderboard")}
            data-testid="view-leaderboard-button"
            className="px-6 py-3 border border-yellow-700 text-yellow-400 hover:bg-yellow-400 hover:text-black font-mono uppercase tracking-widest"
          >
            [ LEADERBOARD ]
          </button>
          <button
            onClick={() => navigate("/")}
            data-testid="home-from-results"
            className="px-6 py-3 border border-green-800 text-green-500 hover:border-green-500 font-mono uppercase tracking-widest"
          >
            [ &lt;&lt; MENU ]
          </button>
        </div>
      </div>
    </TerminalShell>
  );
}
