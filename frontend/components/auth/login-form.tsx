"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ErrorMessage } from "@/components/ui/error-message";

export default function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await apiClient.login({ email, password });
      console.log("Login Success: Token saved", response.access_token);
      toast.success("Successfully logged in!");
      router.push("/dashboard");
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Login failed. Please try again.";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto animate-slide-up">
      <div className="bg-card/80 backdrop-blur-xl rounded-2xl shadow-2xl p-10 border border-border/50 hover:shadow-glow-primary transition-all duration-300">
        {/* Logo/Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 rounded-full gradient-bg flex items-center justify-center shadow-lg">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        <h2 className="text-3xl font-bold text-center mb-2 text-gradient">Welcome Back!</h2>
        <p className="text-center text-muted-foreground mb-8">Sign in to continue to your account</p>

        <ErrorMessage message={error} className="mb-6" />

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-semibold text-foreground">
              Email Address
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </div>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-12 pr-4 py-3.5 border-2 border-input rounded-xl bg-background/50 focus:outline-none focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all duration-200 text-foreground placeholder:text-muted-foreground"
                placeholder="you@example.com"
                disabled={loading}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="block text-sm font-semibold text-foreground">
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-12 pr-4 py-3.5 border-2 border-input rounded-xl bg-background/50 focus:outline-none focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all duration-200 text-foreground placeholder:text-muted-foreground"
                placeholder="••••••••"
                disabled={loading}
                minLength={6}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full gradient-bg text-white py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <LoadingSpinner size="sm" />
                Logging in...
              </span>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-sm text-muted-foreground">
            Don't have an account?{" "}
            <Link href="/register" className="text-primary font-semibold hover:underline hover:text-primary/80 transition-colors">
              Create one now
            </Link>
          </p>
        </div>

        {/* Decorative element */}
        <div className="mt-8 flex items-center justify-center gap-2 text-xs text-muted-foreground">
          <div className="h-px w-12 bg-border"></div>
          <span>Secure Login</span>
          <div className="h-px w-12 bg-border"></div>
        </div>
      </div>
    </div>
  );
}
