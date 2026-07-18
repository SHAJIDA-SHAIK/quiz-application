import React, { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import TerminalShell from "@/components/TerminalShell";
import { api, formatApiErrorDetail } from "@/lib/api";

const TIME_PER_Q = 20;

function AsciiProgress({ current, total }) {
  const filled = Math.floor((current / total) * 20);
  const bar = "#".repeat(filled) + "-".repeat(20 - filled);
  return (
    <div className="font-mono text-green-500 text-sm" data-testid="ascii-progress">
      [{bar}] {current}/{total}
    </div>
  );
}

export default function Quiz() {
  const location = useLocation();
  const navigate = useNavigate();
  const session = location.state?.session;
  const category = location.state?.category;
  const difficulty = location.state?.difficulty;
  const negativeMarking = location.state?.negativeMarking || false;

  useEffect(() => {
    if (!session) navigate("/setup", { replace: true });
  }, [session, navigate]);

  const questions = useMemo(() => session?.questions ?? [], [session]);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState([]); // {question_id, selected_index, time_taken}
  const [selected, setSelected] = useState(null);
  const [timeLeft, setTimeLeft] = useState(TIME_PER_Q);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const startedAtRef = useRef(Date.now());

  // Reset per question
  useEffect(() => {
    setSelected(null);
    setTimeLeft(TIME_PER_Q);
    startedAtRef.current = Date.now();
  }, [idx]);

  // Timer tick
  useEffect(() => {
    if (!questions.length) return;
    if (timeLeft <= 0) return;
    const t = setTimeout(() => setTimeLeft((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [timeLeft, questions.length]);

  // Auto-submit when time runs out
  useEffect(() => {
    if (timeLeft === 0 && questions.length) {
      commitAnswer(null);
    }
  }, [timeLeft]);

  const commitAnswer = (choiceIndex) => {
    if (!questions.length) return;
    const q = questions[idx];
    const timeTaken = Math.max(0, TIME_PER_Q - timeLeft);
    const newAnswers = [
      ...answers,
      { question_id: q.id, selected_index: choiceIndex, time_taken: timeTaken },
    ];
    setAnswers(newAnswers);
    if (idx + 1 < questions.length) {
      setIdx(idx + 1);
    } else {
      submitAll(newAnswers);
    }
  };

  const submitAll = async (final) => {
    setSubmitting(true);
    setError("");
    try {
      const { data } = await api.post("/quiz/submit", {
        quiz_id: session.quiz_id,
        category, difficulty,
        negative_marking: negativeMarking,
        answers: final,
      });
      navigate("/results", { state: { result: data, category, difficulty } });
    } catch (e) {
      setError(formatApiErrorDetail(e.response?.data?.detail) || e.message);
      setSubmitting(false);
    }
  };

  const handleChoose = (i) => {
    if (selected !== null) return;
    setSelected(i);
    // small delay so user sees selection highlight
    setTimeout(() => commitAnswer(i), 150);
  };

  if (!questions.length) return null;

  const q = questions[idx];
  const timerColor =
    timeLeft <= 5 ? "text-red-500 text-glow-red animate-pulse"
    : timeLeft <= 10 ? "text-yellow-400 text-glow-yellow"
    : "text-green-500 text-glow";

  return (
    <TerminalShell>
      <div className="fade-in max-w-4xl" data-testid="quiz-screen">
        {/* Header row */}
        <div className="flex items-center justify-between mb-6 gap-4 flex-wrap">
          <div>
            <div className="text-green-700 text-xs uppercase tracking-widest font-mono">
              [{category} · {difficulty}]
            </div>
            <AsciiProgress current={idx + 1} total={questions.length} />
          </div>
          <div className={`font-mono font-bold text-5xl md:text-6xl ${timerColor}`} data-testid="timer-display">
            {String(timeLeft).padStart(2, "0")}s
          </div>
        </div>

        {/* Question card */}
        <div className="terminal-frame p-6 pt-10 md:p-10 md:pt-14 mb-6 box-glow">
          <div className="text-green-700 text-xs uppercase tracking-widest mb-3 font-mono">
            Q{idx + 1} :: {q.category} :: {q.difficulty}
          </div>
          <h2
            className="text-xl md:text-2xl text-green-300 font-mono leading-relaxed text-glow"
            data-testid="question-text"
          >
            {q.question}
          </h2>
        </div>

        {/* Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="quiz-options">
          {q.options.map((opt, i) => {
            const letter = String.fromCharCode(65 + i);
            const isSel = selected === i;
            return (
              <button
                key={i}
                onClick={() => handleChoose(i)}
                disabled={selected !== null || submitting}
                data-testid={`option-${letter}`}
                className={`text-left p-4 md:p-5 border font-mono transition-none ${
                  isSel
                    ? "bg-green-500 text-black border-green-500 text-glow"
                    : "bg-black/60 text-green-400 border-green-800 hover:border-green-500 hover:bg-green-950/40"
                } disabled:opacity-70 disabled:cursor-not-allowed`}
              >
                <span className={`font-bold mr-3 ${isSel ? "text-black" : "text-yellow-400"}`}>[{letter}]</span>
                {opt}
              </button>
            );
          })}
        </div>

        <div className="mt-6 flex justify-between items-center">
          <button
            onClick={() => commitAnswer(null)}
            disabled={selected !== null || submitting}
            data-testid="skip-question-button"
            className="text-green-700 font-mono text-sm uppercase tracking-widest hover:text-green-400 disabled:opacity-50"
          >
            &gt; skip / next
          </button>
          {submitting && (
            <div className="text-yellow-400 font-mono cursor-blink" data-testid="submitting-indicator">
              PROCESSING RESULTS
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 text-red-400 font-mono text-sm text-glow-red" data-testid="quiz-error">
            ! ERROR: {error}
          </div>
        )}
      </div>
    </TerminalShell>
  );
}
