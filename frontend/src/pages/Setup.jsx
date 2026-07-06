import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import TerminalShell from "@/components/TerminalShell";
import { api, formatApiErrorDetail } from "@/lib/api";

const CATEGORIES = ["Python", "DBMS", "OS", "Aptitude", "Mixed"];
const DIFFICULTIES = ["Easy", "Medium", "Hard", "Mixed"];

const OptionButton = ({ selected, onClick, children, testId }) => (
  <button
    onClick={onClick}
    data-testid={testId}
    className={`px-4 py-3 border font-mono uppercase tracking-widest text-sm transition-none ${
      selected
        ? "bg-green-500 text-black border-green-500 text-glow"
        : "bg-black text-green-400 border-green-800 hover:border-green-500"
    }`}
  >
    {selected ? "[X]" : "[ ]"} {children}
  </button>
);

export default function Setup() {
  const navigate = useNavigate();
  const [category, setCategory] = useState("Python");
  const [difficulty, setDifficulty] = useState("Easy");
  const [numQuestions, setNumQuestions] = useState(10);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const start = async () => {
    setError("");
    setBusy(true);
    try {
      const { data } = await api.post("/quiz/start", {
        category, difficulty, num_questions: numQuestions,
      });
      navigate("/quiz", { state: { session: data, category, difficulty } });
    } catch (e) {
      setError(formatApiErrorDetail(e.response?.data?.detail) || e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <TerminalShell>
      <div className="fade-in max-w-3xl">
        <div className="text-green-700 text-xs mb-2 font-mono uppercase tracking-widest">[configure_session]</div>
        <h1 className="text-3xl md:text-5xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow mb-8">
          === QUIZ SETUP ===
        </h1>

        <section className="mb-8 terminal-frame p-6 pt-10">
          <div className="text-green-600 text-xs uppercase tracking-widest mb-4 font-mono">&gt; select category</div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3" data-testid="category-options">
            {CATEGORIES.map((c) => (
              <OptionButton key={c} selected={category === c} onClick={() => setCategory(c)} testId={`category-${c.toLowerCase()}`}>
                {c}
              </OptionButton>
            ))}
          </div>
        </section>

        <section className="mb-8 terminal-frame p-6 pt-10">
          <div className="text-green-600 text-xs uppercase tracking-widest mb-4 font-mono">&gt; select difficulty</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="difficulty-options">
            {DIFFICULTIES.map((d) => (
              <OptionButton key={d} selected={difficulty === d} onClick={() => setDifficulty(d)} testId={`difficulty-${d.toLowerCase()}`}>
                {d}
              </OptionButton>
            ))}
          </div>
        </section>

        <section className="mb-8 terminal-frame p-6 pt-10">
          <div className="text-green-600 text-xs uppercase tracking-widest mb-4 font-mono">&gt; questions per session</div>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min={5}
              max={20}
              step={1}
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
              data-testid="num-questions-slider"
              className="flex-1 accent-green-500"
            />
            <span className="font-mono text-2xl text-yellow-400 text-glow-yellow w-14 text-center" data-testid="num-questions-value">
              {numQuestions}
            </span>
          </div>
        </section>

        {error && (
          <div className="mb-4 text-red-400 font-mono text-sm text-glow-red" data-testid="setup-error">
            ! ERROR: {error}
          </div>
        )}

        <div className="flex flex-col md:flex-row gap-3">
          <button
            onClick={start}
            disabled={busy}
            data-testid="start-quiz-button"
            className="px-8 py-4 border border-green-500 bg-black text-green-400 hover:bg-green-500 hover:text-black font-mono uppercase tracking-widest text-glow disabled:opacity-50"
          >
            {busy ? "[ INITIALIZING... ]" : "[ ▶ BEGIN QUIZ ]"}
          </button>
          <button
            onClick={() => navigate("/")}
            data-testid="cancel-setup"
            className="px-8 py-4 border border-green-800 text-green-500 hover:border-green-500 font-mono uppercase tracking-widest"
          >
            [ &lt;&lt; BACK ]
          </button>
        </div>
      </div>
    </TerminalShell>
  );
}
