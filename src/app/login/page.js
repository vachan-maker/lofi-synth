"use client";
import {
  User,
  LockKeyhole,
  Eye,
  EyeOff,
  AlertCircle,
  Mail,
  CheckCircle,
} from "lucide-react";
import React, { useState } from "react";
import { Orbitron } from "next/font/google";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";

const orbitron = Orbitron({
  subsets: ["latin"],
});

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function LogIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [resetMessage, setResetMessage] = useState("");

  const router = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (!username || !password) {
      setError("Username and Password are required");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/auth/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        router.push("/dashboard");
      } else {
        setError(data.error || "Login failed");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResetMessage("");

    if (!resetEmail) {
      setError("Please enter your email address");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/auth/forgot-password/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: resetEmail }),
      });

      const data = await response.json();

      if (response.ok) {
        setResetMessage(data.message || "Reset link sent successfully.");
        setResetEmail("");
      } else {
        setError(data.error || "Failed to send reset email");
      }
    } catch (err) {
      console.error("Password reset error:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-dvh bg-[url(/1.png)] bg-cover bg-no-repeat flex items-center justify-center p-4">
      <div className="flex flex-col md:flex-row items-center justify-between max-w-7xl mx-auto gap-8">
        <div className="w-full md:w-auto">
          <Image
            src="/enhanced.png"
            alt="Enhanced"
            width={500}
            height={500}
            className="w-full max-w-lg"
            priority
          />
        </div>

        <div className="bg-black/20 p-8 rounded-xl max-w-md w-full">
          <h1
            className={`${orbitron.className} text-5xl md:text-7xl text-[#fffbfb] mb-8 text-center`}
          >
            {showForgotPassword ? "Reset Password" : "Welcome Back"}
          </h1>

          {error && (
            <div className="flex items-center gap-2 bg-red-500/20 border border-red-500 text-red-200 p-3 rounded-lg mb-4">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          )}

          {resetMessage && (
            <div className="flex items-center gap-2 bg-green-500/20 border border-green-500 text-green-200 p-3 rounded-lg mb-4">
              <CheckCircle className="w-5 h-5" />
              <span>{resetMessage}</span>
            </div>
          )}

          {!showForgotPassword ? (
            <form onSubmit={handleLogin} className="flex flex-col gap-4">
              <div className="relative flex items-center">
                <User className="absolute left-3 w-5 h-5 text-gray-600" />
                <input
                  type="text"
                  placeholder="Username"
                  aria-label="Username"
                  className="pl-10 p-2 border-2 border-gray-300 rounded-lg w-full text-gray-800 bg-white/90"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              <div className="relative flex items-center">
                <LockKeyhole className="absolute left-3 w-5 h-5 text-gray-600" />
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Password"
                  aria-label="Password"
                  className="pl-10 pr-10 p-2 border-2 border-gray-300 rounded-lg w-full text-gray-800 bg-white/90"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute right-3"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5 text-gray-600" />
                  ) : (
                    <Eye className="w-5 h-5 text-gray-600" />
                  )}
                </button>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white p-2 rounded-lg font-medium transition-colors"
              >
                {loading ? "Signing In..." : "Sign In"}
              </button>

              <div className="flex justify-between items-center text-sm">
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  className="text-[#fffbfb] hover:underline"
                >
                  Forgot Password?
                </button>
                <span className="text-[#fffbfb]">
                  Don't have an account?
                  <Link href="/signup" className="ml-1 hover:underline">
                    Sign up
                  </Link>
                </span>
              </div>
            </form>
          ) : (
            <form onSubmit={handleForgotPassword} className="flex flex-col gap-4">
              <div className="relative flex items-center">
                <Mail className="absolute left-3 w-5 h-5 text-gray-600" />
                <input
                  type="email"
                  placeholder="Enter your email address"
                  aria-label="Email address for password reset"
                  className="pl-10 p-2 border-2 border-gray-300 rounded-lg w-full text-gray-800 bg-white/90"
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white p-2 rounded-lg font-medium transition-colors"
              >
                {loading ? "Sending..." : "Send Reset Link"}
              </button>

              <button
                type="button"
                onClick={() => {
                  setShowForgotPassword(false);
                  setError("");
                  setResetMessage("");
                }}
                className="text-[#fffbfb] hover:underline text-sm"
              >
                ← Back to Login
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
