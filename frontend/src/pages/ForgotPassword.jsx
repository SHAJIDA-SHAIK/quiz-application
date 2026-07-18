import React, { useState } from "react";
import { Link } from "react-router-dom";
import { api, formatApiErrorDetail } from "@/lib/api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [devLink, setDevLink] = useState(null);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setBusy(true); setError(""); setDevLink(null);
    try {
      const { data } = await api.post("/auth/forgot-password", { email });
      setDone(true);
      if (data.dev_reset_link) setDevLink(data.dev_reset_link);
    } catch (err) {
      setError(formatApiErrorDetail(err.response?.data?.detail) || err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen relative z-10 flex items-center justify-center px-4 py-12 crt-flicker">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-green-700 text-xs mb-2 font-mono">-- ACCOUNT RECOVERY --</div>
          <h1 className="text-4xl md:text-5xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow-strong">
            FORGOT<span className="text-yellow-400">::</span>PW
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="terminal-frame p-8 pt-10 box-glow" data-testid="forgot-password-form">
          <div className="mb-5">
            <label className="block text-xs uppercase tracking-widest text-green-600 mb-2 font-mono">&gt; email</label>
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              data-testid="forgot-email-input"
              className="w-full bg-transparent border-0 border-b border-green-800 focus:border-green-500 focus:outline-none text-green-400 font-mono py-2 placeholder:text-green-900"
              placeholder="user@quiz.sys"
            />
          </div>

          {error && <div className="mb-4 text-red-400 text-sm font-mono text-glow-red" data-testid="forgot-error">! {error}</div>}

          <button type="submit" disabled={busy} data-testid="forgot-submit-button"
            className="w-full py-3 border border-green-500 bg-black text-green-400 hover:bg-green-500 hover:text-black font-mono uppercase tracking-widest text-glow disabled:opacity-50">
            {busy ? "[ TRANSMITTING... ]" : "[ REQUEST RESET LINK ]"}
          </button>

          {done && (
            <div className="mt-6 border border-green-700 bg-black/60 p-4 font-mono text-sm text-green-400" data-testid="forgot-success">
              <div className="text-green-500 mb-2 text-glow">&gt; if that email exists, a reset link was created.</div>
              {devLink ? (
                <>
                  <div className="text-green-600 text-xs mb-1">DEV MODE: reset link (click to open)</div>
                  <a href={devLink} data-testid="dev-reset-link" className="text-yellow-400 hover:text-yellow-300 break-all underline decoration-dotted">{devLink}</a>
                </>
              ) : (
                <div className="text-green-600 text-xs">Check your inbox — but in this demo build, no email is sent unless a matching account exists.</div>
              )}
            </div>
          )}

          <div className="mt-6 text-center text-green-700 text-sm font-mono">
            <Link to="/login" data-testid="back-to-login" className="text-yellow-400 hover:text-yellow-300 underline decoration-dotted">&lt;&lt; back to login</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
