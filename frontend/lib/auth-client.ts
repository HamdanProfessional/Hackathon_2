/**
 * Better Auth Client
 *
 * This file provides the Better Auth client configured for our FastAPI backend.
 * The client handles sign in, sign up, sign out, and session management.
 */

import { createAuthClient } from "better-auth/client";

/**
 * Better Auth Client Instance
 *
 * The baseURL points to our Next.js API routes which bridge to FastAPI
 */
export const authClient = createAuthClient({
  baseURL: typeof window !== "undefined"
    ? window.location.origin // Use current origin for API routes
    : "http://localhost:3000",
});

/**
 * Type definitions for our user
 */
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

export interface Session {
  token: string;
  expiresAt: Date;
  user: User;
}

/**
 * Sign in with email and password
 */
export async function signIn(email: string, password: string) {
  const response = await authClient.signIn.email({
    email,
    password,
  });

  // Store JWT token for API calls
  // Note: better-auth response structure has token at data level
  if ((response.data as any)?.token) {
    localStorage.setItem("access_token", (response.data as any).token);
  }

  return response;
}

/**
 * Sign up with email, password, and optional name
 */
export async function signUp(email: string, password: string, name?: string) {
  const response = await authClient.signUp.email({
    email,
    password,
    name: name || email.split('@')[0], // Use email username as default name
  });

  // Store JWT token for API calls
  if ((response.data as any)?.token) {
    localStorage.setItem("access_token", (response.data as any).token);
  }

  return response;
}

/**
 * Sign out and clear session
 */
export async function signOut() {
  const response = await authClient.signOut();

  // Clear local storage
  localStorage.removeItem("access_token");

  // Redirect to login
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }

  return response;
}

/**
 * Get current session from server
 * This validates the JWT token with the backend
 */
export async function getSession() {
  const response = await authClient.getSession();

  // Update localStorage token if session exists
  // Note: better-auth response structure varies
  if ((response.data as any)?.token) {
    localStorage.setItem("access_token", (response.data as any).token);
  }

  return response;
}

/**
 * Get JWT token for API calls
 */
export function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("access_token");
  }
  return null;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

/**
 * Get current user from session (client-side helper)
 */
export async function getCurrentUser(): Promise<User | null> {
  const session = await getSession();
  return (session.data as any)?.session?.user || null;
}
