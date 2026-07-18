import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import TerminalShell from "@/components/TerminalShell";
import { useAuth } from "@/context/AuthContext";
import { api, formatApiErrorDetail } from "@/lib/api";

const CATS = ["Python", "DBMS", "OS", "Aptitude"];
const DIFFS = ["Easy", "Medium", "Hard"];

function Section({ title, children, testId }) {
  return (
    <section className="terminal-frame p-6 pt-10 mb-8" data-testid={testId}>
      <h2 className="text-lg font-mono uppercase tracking-widest text-green-500 text-glow mb-4">&gt; {title}</h2>
      {children}
    </section>
  );
}

function AnalyticsPanel({ data }) {
  if (!data) return <div className="text-green-500 font-mono cursor-blink">LOADING TELEMETRY</div>;
  const bar = (v) => {
    const filled = Math.round((v / 100) * 20);
    return "#".repeat(filled) + "-".repeat(20 - filled);
  };
  return (
    <div className="font-mono text-sm space-y-6" data-testid="admin-analytics">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          ["Users", data.total_users, "text-green-400"],
          ["Verified", data.verified_users, "text-yellow-400"],
          ["Games", data.total_games, "text-green-400"],
          ["Admin Qs", data.total_admin_questions, "text-green-400"],
          ["Avg Acc%", data.overall_avg_accuracy, "text-yellow-400"],
        ].map(([label, v, cls]) => (
          <div key={label} className="border border-green-800 bg-black/60 p-3">
            <div className="text-xs text-green-700 uppercase">{label}</div>
            <div className={`text-2xl font-bold ${cls} text-glow`} data-testid={`stat-${label.toLowerCase().replace(/[^a-z]/g,"")}`}>{v}</div>
          </div>
        ))}
      </div>

      <div>
        <div className="text-green-600 uppercase text-xs mb-2">by category</div>
        {data.by_category.length === 0 ? <div className="text-green-700">&gt; no games yet</div> : (
          <div className="space-y-2">
            {data.by_category.map((c) => (
              <div key={c.category} className="border-b border-green-900 py-1">
                <div className="flex justify-between text-green-400"><span>{c.category}</span><span>{c.games} games · avg {c.avg_accuracy}%</span></div>
                <div className="text-green-500 text-xs">[{bar(c.avg_accuracy)}]</div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <div className="text-green-600 uppercase text-xs mb-2">top players</div>
        {data.top_players.length === 0 ? <div className="text-green-700">&gt; empty</div> : (
          <table className="w-full text-sm">
            <tbody>
              {data.top_players.map((p, i) => (
                <tr key={p.user_id} className="border-b border-green-900">
                  <td className="py-1 text-yellow-400 font-bold">#{i + 1}</td>
                  <td className="py-1 text-green-300">{p.user_name}</td>
                  <td className="py-1 text-right text-green-500">best: <span className="text-yellow-400 font-bold">{p.best_score}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default function Admin() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [error, setError] = useState("");
  // Question creator
  const [category, setCategory] = useState("Python");
  const [difficulty, setDifficulty] = useState("Easy");
  const [qText, setQText] = useState("");
  const [opts, setOpts] = useState(["", "", "", ""]);
  const [correctIdx, setCorrectIdx] = useState(0);
  const [busy, setBusy] = useState(false);
  // AI generator
  const [aiTopic, setAiTopic] = useState("Data Structures");
  const [aiDiff, setAiDiff] = useState("Medium");
  const [aiCount, setAiCount] = useState(3);
  const [aiBusy, setAiBusy] = useState(false);
  const [aiResults, setAiResults] = useState([]);
  const [aiError, setAiError] = useState("");

  const reload = async () => {
    try {
      const [a, q] = await Promise.all([
        api.get("/admin/analytics"),
        api.get("/admin/questions"),
      ]);
      setAnalytics(a.data);
      setQuestions(q.data);
    } catch (e) {
      setError(formatApiErrorDetail(e.response?.data?.detail) || e.message);
    }
  };

  useEffect(() => { reload(); }, []);

  if (user && user.role !== "admin") return <Navigate to="/" replace />;

  const addQuestion = async (e) => {
    e?.preventDefault();
    setError(""); setBusy(true);
    try {
      await api.post("/admin/questions", {
        category, difficulty, question: qText, options: opts, correct_index: correctIdx,
      });
      setQText(""); setOpts(["", "", "", ""]); setCorrectIdx(0);
      await reload();
    } catch (e) {
      setError(formatApiErrorDetail(e.response?.data?.detail) || e.message);
    } finally {
      setBusy(false);
    }
  };

  const removeQuestion = async (id) => {
    try {
      await api.delete(`/admin/questions/${id}`);
      await reload();
    } catch (e) {
      setError(formatApiErrorDetail(e.response?.data?.detail) || e.message);
    }
  };

  const runAI = async () => {
    setAiBusy(true); setAiError(""); setAiResults([]);
    try {
      const { data } = await api.post("/admin/ai-generate", {
        topic: aiTopic, difficulty: aiDiff, count: aiCount,
      });
      setAiResults(data.questions);
    } catch (e) {
      setAiError(formatApiErrorDetail(e.response?.data?.detail) || e.message);
    } finally {
      setAiBusy(false);
    }
  };

  const saveAIQuestion = async (q) => {
    try {
      await api.post("/admin/questions", {
        category: aiTopic in { Python:1, DBMS:1, OS:1, Aptitude:1 } ? aiTopic : "Python",
        difficulty: aiDiff, question: q.question, options: q.options, correct_index: q.correct_index,
      });
      setAiResults((prev) => prev.filter((x) => x !== q));
      await reload();
    } catch (e) {
      setAiError(formatApiErrorDetail(e.response?.data?.detail) || e.message);
    }
  };

  return (
    <TerminalShell>
      <div className="fade-in max-w-5xl">
        <div className="text-green-700 text-xs uppercase tracking-widest mb-2 font-mono">[root@retroquiz ~]#</div>
        <h1 className="text-3xl md:text-5xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow-strong mb-8">
          === ADMIN CONSOLE ===
        </h1>

        {error && <div className="mb-4 text-red-400 font-mono text-sm text-glow-red" data-testid="admin-error">! {error}</div>}

        <Section title="analytics" testId="section-analytics"><AnalyticsPanel data={analytics} /></Section>

        <Section title="ai question generator [gemini-3-flash]" testId="section-ai">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
            <input value={aiTopic} onChange={(e)=>setAiTopic(e.target.value)} data-testid="ai-topic-input"
              placeholder="topic (e.g. Data Structures)"
              className="md:col-span-2 bg-black border border-green-800 focus:border-green-500 text-green-400 font-mono px-3 py-2"/>
            <select value={aiDiff} onChange={(e)=>setAiDiff(e.target.value)} data-testid="ai-diff-select"
              className="bg-black border border-green-800 text-green-400 font-mono px-3 py-2">
              {DIFFS.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
            <input type="number" min={1} max={10} value={aiCount} onChange={(e)=>setAiCount(Number(e.target.value))} data-testid="ai-count-input"
              className="bg-black border border-green-800 text-green-400 font-mono px-3 py-2"/>
          </div>
          <button onClick={runAI} disabled={aiBusy} data-testid="ai-generate-button"
            className="px-6 py-2 border border-yellow-500 text-yellow-400 hover:bg-yellow-400 hover:text-black font-mono uppercase tracking-widest text-glow-yellow disabled:opacity-50">
            {aiBusy ? "[ GEMINI THINKING... ]" : "[ ▶ GENERATE WITH AI ]"}
          </button>
          {aiError && <div className="mt-3 text-red-400 font-mono text-sm text-glow-red" data-testid="ai-error">! {aiError}</div>}
          {aiResults.length > 0 && (
            <div className="mt-6 space-y-3" data-testid="ai-results">
              {aiResults.map((q, i) => (
                <div key={i} className="border border-green-800 bg-black/60 p-3 font-mono text-sm">
                  <div className="text-green-300 mb-2">{q.question}</div>
                  <ul className="text-xs space-y-1 mb-2">
                    {q.options.map((o, oi) => (
                      <li key={oi} className={oi === q.correct_index ? "text-green-400 text-glow" : "text-green-700"}>
                        [{String.fromCharCode(65+oi)}] {o} {oi === q.correct_index && "← correct"}
                      </li>
                    ))}
                  </ul>
                  <button onClick={()=>saveAIQuestion(q)} data-testid={`save-ai-${i}`}
                    className="px-3 py-1 border border-green-500 text-green-400 hover:bg-green-500 hover:text-black text-xs uppercase">+ save to bank</button>
                </div>
              ))}
            </div>
          )}
        </Section>

        <Section title="add question manually" testId="section-add-question">
          <form onSubmit={addQuestion} className="font-mono space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <select value={category} onChange={(e)=>setCategory(e.target.value)} data-testid="new-q-category"
                className="bg-black border border-green-800 text-green-400 px-3 py-2">
                {CATS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
              <select value={difficulty} onChange={(e)=>setDifficulty(e.target.value)} data-testid="new-q-difficulty"
                className="bg-black border border-green-800 text-green-400 px-3 py-2">
                {DIFFS.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <input required value={qText} onChange={(e)=>setQText(e.target.value)} data-testid="new-q-text"
              placeholder="question text"
              className="w-full bg-black border border-green-800 focus:border-green-500 text-green-400 px-3 py-2"/>
            {opts.map((o, i) => (
              <div key={i} className="flex gap-2 items-center">
                <input type="radio" checked={correctIdx===i} onChange={()=>setCorrectIdx(i)} data-testid={`new-q-correct-${i}`}
                  className="accent-green-500"/>
                <span className="text-yellow-400 w-5">[{String.fromCharCode(65+i)}]</span>
                <input required value={o} onChange={(e)=>{const n=[...opts]; n[i]=e.target.value; setOpts(n);}}
                  data-testid={`new-q-option-${i}`}
                  className="flex-1 bg-black border border-green-800 focus:border-green-500 text-green-400 px-3 py-2"/>
              </div>
            ))}
            <button type="submit" disabled={busy} data-testid="new-q-submit"
              className="px-6 py-2 border border-green-500 text-green-400 hover:bg-green-500 hover:text-black uppercase tracking-widest text-glow disabled:opacity-50">
              {busy ? "[ SAVING... ]" : "[ + ADD QUESTION ]"}
            </button>
          </form>
        </Section>

        <Section title={`saved admin questions (${questions.length})`} testId="section-questions-list">
          {questions.length === 0 ? <div className="text-green-700 font-mono">&gt; empty</div> : (
            <div className="space-y-2 font-mono text-sm" data-testid="admin-questions-list">
              {questions.map((q) => (
                <div key={q.id} className="border border-green-800 bg-black/60 p-3 flex justify-between gap-3">
                  <div>
                    <div className="text-green-700 text-xs">[{q.category} · {q.difficulty}]</div>
                    <div className="text-green-300">{q.question}</div>
                    <div className="text-xs text-green-600 mt-1">
                      {q.options.map((o,i)=>(
                        <span key={i} className={i===q.correct_index ? "text-green-400 mr-3" : "mr-3"}>
                          [{String.fromCharCode(65+i)}] {o}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button onClick={()=>removeQuestion(q.id)} data-testid={`delete-q-${q.id}`}
                    className="px-3 py-1 border border-red-700 text-red-400 hover:bg-red-500 hover:text-black text-xs uppercase h-fit">del</button>
                </div>
              ))}
            </div>
          )}
        </Section>
      </div>
    </TerminalShell>
  );
}
