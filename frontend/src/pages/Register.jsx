import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, formatApiErrorDetail } from "@/context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [verifyLink, setVerifyLink] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const data = await register(name, email, password);
      if (data?.dev_verify_link) {
        setVerifyLink(data.dev_verify_link);
        // give the user a moment to see it before navigating
        setTimeout(() => navigate("/"), 1200);
      } else {
        navigate("/");
      }
    } catch (err) {
      setError(formatApiErrorDetail(err.response?.data?.detail) || err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen relative z-10 flex items-center justify-center px-4 py-12 crt-flicker">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="text-green-700 text-xs mb-2 font-mono">-- NEW USER PROVISION --</div>
          <h1 className="text-4xl md:text-5xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow-strong">
            REGISTER<span className="text-yellow-400">::</span>PLAYER
          </h1>
          <div className="text-green-600 text-sm mt-3 font-mono">
            <span className="text-green-700">&gt;</span> CREATE ACCESS CREDENTIALS<span className="cursor-blink"></span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="terminal-frame p-8 pt-10 box-glow" data-testid="register-form">
          <div className="mb-5">
            <label className="block text-xs uppercase tracking-widest text-green-600 mb-2 font-mono">&gt; name</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              data-testid="register-name-input"
              className="w-full bg-transparent border-0 border-b border-green-800 focus:border-green-500 focus:outline-none text-green-400 font-mono py-2 placeholder:text-green-900"
              placeholder="commander_x"
            />
          </div>
          <div className="mb-5">
            <label className="block text-xs uppercase tracking-widest text-green-600 mb-2 font-mono">&gt; email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              data-testid="register-email-input"
              className="w-full bg-transparent border-0 border-b border-green-800 focus:border-green-500 focus:outline-none text-green-400 font-mono py-2 placeholder:text-green-900"
              placeholder="user@quiz.sys"
            />
          </div>
          <div className="mb-6">
            <label className="block text-xs uppercase tracking-widest text-green-600 mb-2 font-mono">&gt; password (min 6)</label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              data-testid="register-password-input"
              className="w-full bg-transparent border-0 border-b border-green-800 focus:border-green-500 focus:outline-none text-green-400 font-mono py-2 placeholder:text-green-900"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="mb-4 text-red-400 text-sm font-mono text-glow-red" data-testid="register-error">
              ! ERROR: {error}
            </div>
          )}

          {verifyLink && (
            <div className="mb-4 border border-green-700 bg-black/60 p-3 text-xs font-mono" data-testid="verify-link-banner">
              <div className="text-green-500 mb-1">&gt; ACCOUNT CREATED — verify email:</div>
              <a href={verifyLink} className="text-yellow-400 hover:text-yellow-300 break-all underline decoration-dotted" data-testid="dev-verify-link">
                {verifyLink}
              </a>
            </div>
          )}

          <button
            type="submit"
            disabled={busy}
            data-testid="register-submit-button"
            className="w-full py-3 border border-green-500 bg-black text-green-400 hover:bg-green-500 hover:text-black transition-none font-mono uppercase tracking-widest text-glow disabled:opacity-50"
          >
            {busy ? "[ CREATING... ]" : "[ INITIALIZE ACCOUNT ]"}
          </button>

          <div className="mt-6 text-center text-green-700 text-sm font-mono">
            already registered?{" "}
            <Link to="/login" data-testid="go-to-login" className="text-yellow-400 hover:text-yellow-300 underline decoration-dotted">
              &lt;&lt; login
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
