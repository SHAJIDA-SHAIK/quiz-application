import React, { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { api, formatApiErrorDetail } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function VerifyEmail() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const { refresh } = useAuth();
  const [status, setStatus] = useState("verifying"); // verifying | ok | error
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMsg("Missing verification token");
      return;
    }
    (async () => {
      try {
        await api.post("/auth/verify-email", { token });
        setStatus("ok");
        setMsg("Email verified successfully.");
        refresh?.();
      } catch (err) {
        setStatus("error");
        setMsg(formatApiErrorDetail(err.response?.data?.detail) || err.message);
      }
    })();
  }, [token, refresh]);

  return (
    <div className="min-h-screen relative z-10 flex items-center justify-center px-4 py-12 crt-flicker">
      <div className="terminal-frame p-10 pt-14 w-full max-w-lg text-center" data-testid="verify-email-page">
        <div className="text-green-700 text-xs mb-2 font-mono">-- EMAIL VERIFICATION --</div>
        <h1 className="text-3xl font-bold font-mono uppercase tracking-widest text-green-500 text-glow mb-6">
          VERIFY::EMAIL
        </h1>
        {status === "verifying" && (
          <div className="text-green-400 font-mono cursor-blink" data-testid="verify-status">CHECKING TOKEN</div>
        )}
        {status === "ok" && (
          <>
            <div className="text-green-400 text-glow font-mono text-xl mb-4" data-testid="verify-status">✓ {msg}</div>
            <Link to="/" className="inline-block px-6 py-3 border border-green-500 hover:bg-green-500 hover:text-black text-green-400 font-mono uppercase tracking-widest text-glow" data-testid="verify-continue">
              [ CONTINUE ]
            </Link>
          </>
        )}
        {status === "error" && (
          <>
            <div className="text-red-400 text-glow-red font-mono mb-4" data-testid="verify-status">! {msg}</div>
            <Link to="/" className="text-yellow-400 hover:text-yellow-300 underline decoration-dotted font-mono">go home</Link>
          </>
        )}
      </div>
    </div>
  );
}
