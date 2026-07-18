import React, { useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { api, formatApiErrorDetail } from "@/lib/api";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [ok, setOk] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (password.length < 6) return setError("Password must be at least 6 characters");
    if (password !== confirm) return setError("Passwords do not match");
    setBusy(true);
    try {
      await api.post("/auth/reset-password", { token, new_password: password });
      setOk(true);
      setTimeout(() => navigate("/login"), 2000);
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
          <div className="text-green-700 text-xs mb-2 font-mono">-- SET NEW CREDENTIALS --</div>
          <h1 className="text-4xl md:text-5xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow-strong">
            RESET<span className="text-yellow-400">::</span>PW
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="terminal-frame p-8 pt-10 box-glow" data-testid="reset-password-form">
          {!token && (
            <div className="text-red-400 font-mono text-sm mb-4 text-glow-red" data-testid="no-token-error">! no reset token in URL</div>
          )}
          <div className="mb-5">
            <label className="block text-xs uppercase tracking-widest text-green-600 mb-2 font-mono">&gt; new password (min 6)</label>
            <input
              type="password" required minLength={6} value={password} onChange={(e) => setPassword(e.target.value)}
              data-testid="reset-password-input"
              className="w-full bg-transparent border-0 border-b border-green-800 focus:border-green-500 focus:outline-none text-green-400 font-mono py-2"
            />
          </div>
          <div className="mb-6">
            <label className="block text-xs uppercase tracking-widest text-green-600 mb-2 font-mono">&gt; confirm password</label>
            <input
              type="password" required minLength={6} value={confirm} onChange={(e) => setConfirm(e.target.value)}
              data-testid="reset-confirm-input"
              className="w-full bg-transparent border-0 border-b border-green-800 focus:border-green-500 focus:outline-none text-green-400 font-mono py-2"
            />
          </div>

          {error && <div className="mb-4 text-red-400 text-sm font-mono text-glow-red" data-testid="reset-error">! {error}</div>}
          {ok && <div className="mb-4 text-green-400 text-sm font-mono text-glow" data-testid="reset-success">&gt; password updated. redirecting to login...</div>}

          <button type="submit" disabled={busy || !token || ok} data-testid="reset-submit-button"
            className="w-full py-3 border border-green-500 bg-black text-green-400 hover:bg-green-500 hover:text-black font-mono uppercase tracking-widest text-glow disabled:opacity-50">
            {busy ? "[ UPDATING... ]" : "[ UPDATE PASSWORD ]"}
          </button>

          <div className="mt-6 text-center text-green-700 text-sm font-mono">
            <Link to="/login" className="text-yellow-400 hover:text-yellow-300 underline decoration-dotted">&lt;&lt; back to login</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
