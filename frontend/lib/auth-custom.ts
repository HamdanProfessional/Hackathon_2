/**
 * Better Auth Custom Backend Adapter
 *
 * This file provides custom auth functions that integrate Better Auth
 * with our FastAPI Python backend.
 */

import { betterAuth } from "better-auth";

/**
 * Custom backend URLs
 */
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Custom auth functions that call our FastAPI backend
 *
 * These functions are used by the Better Auth client to interact
 * with our Python backend instead of a direct database connection.
 */

export async function customSignIn(email: string, password: string) {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Login failed");
  }

  const data = await response.json();

  // Store the token in localStorage for API calls
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", data.access_token);
  }

  return {
    user: data.user,
    session: {
      token: data.access_token,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    },
  };
}

export async function customSignUp(email: string, password: string, name?: string) {
  const response = await fetch(`${API_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Registration failed");
  }

  const data = await response.json();

  // Store the token in localStorage for API calls
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", data.access_token);
  }

  return {
    user: data.user,
    session: {
      token: data.access_token,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    },
  };
}

export async function customSignOut() {
  // Clear local storage
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  }

  return { success: true };
}

export async function customGetSession() {
  const token = typeof window !== "undefined"
    ? localStorage.getItem("access_token")
    : null;

  if (!token) {
    return null;
  }

  try {
    // Verify token by calling backend
    const response = await fetch(`${API_URL}/api/auth/me`, {
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      // Token is invalid, clear it
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
      }
      return null;
    }

    const user = await response.json();

    return {
      user,
      session: {
        token,
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      },
    };
  } catch {
    return null;
  }
}

/**
 * Better Auth instance with custom backend integration
 *
 * This configuration uses custom functions instead of direct database access,
 * allowing Better Auth to work with our FastAPI Python backend.
 */
export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",

  // Disable default database since we use custom backend
  database: {
    provider: "custom",
  },

  // Email & password with custom handlers
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
    sendResetPassword: async ({ user, url }: any) => {
      console.log("Password reset for:", user.email);
    },
    sendVerificationEmail: async ({ user, url }: any) => {
      console.log("Verification for:", user.email);
    },
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60,
    },
  },

  advanced: {
    useSecureCookies: process.env.NODE_ENV === "production",
    cookiePrefix: "todo_app",
  },
});

export type Session = typeof auth.$Infer.Session;
// User type is not directly exported by better-auth, define it manually
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
  updatedAt: Date;
  emailVerified: boolean;
  image?: string | null;
}
