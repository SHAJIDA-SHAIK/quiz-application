import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api, formatApiErrorDetail } from "@/lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // user: null = checking, false = unauthenticated, object = authenticated
  const [user, setUser] = useState(null);

  const check = useCallback(async () => {
    try {
      const { data } = await api.get("/auth/me");
      setUser(data);
    } catch {
      setUser(false);
    }
  }, []);

  useEffect(() => {
    check();
  }, [check]);

  const login = async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    setUser(data);
    return data;
  };

  const register = async (name, email, password) => {
    const { data } = await api.post("/auth/register", { name, email, password });
    setUser(data);
    return data;
  };

  const logout = async () => {
    try { await api.post("/auth/logout"); } catch { /* ignore logout errors */ }
    setUser(false);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, refresh: check }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

export { formatApiErrorDetail };
