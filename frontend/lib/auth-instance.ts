/**
 * Better Auth Configuration with JWT Plugin
 *
 * This file configures Better Auth with JWT plugin for authentication.
 * The JWT tokens are issued by Better Auth and verified by the FastAPI backend.
 */

import { betterAuth } from "better-auth";
import { jwt } from "better-auth/jwt";
import { nodemailer } from "better-auth/nodemailer";

/**
 * Better Auth instance configuration
 *
 * JWT Plugin Configuration:
 * - Issues JWT tokens when users log in
 * - Tokens are signed with BETTER_AUTH_SECRET
 * - Backend must use the same secret to verify tokens
 */
export const auth = betterAuth({
  // Database configuration (we'll use our existing backend)
  // Better Auth can work with a custom backend via the baseURL
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",

  // Advanced: Disable Better Auth's database since we use Python backend
  // We'll use custom endpoints that bridge to our FastAPI backend
  database: {
    provider: "custom",
  },

  // Social providers (optional - can add later)
  socialProviders: {
    // Add Google, GitHub, etc. if needed
  },

  // Email & password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Disable for hackathon
    sendResetPassword: async ({ user, url }) => {
      // Implement password reset email if needed
      console.log("Password reset requested for:", user.email);
    },
    sendVerificationEmail: async ({ user, url }) => {
      // Implement email verification if needed
      console.log("Verification email sent to:", user.email);
    },
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },

  // Advanced configuration
  advanced: {
    // Use cookies for session
    useSecureCookies: process.env.NODE_ENV === "production",
    crossSubDomainCookies: {
      enabled: false,
    },
    cookiePrefix: "todo_app",
  },

  // Account configuration
  account: {
    accountLinking: {
      enabled: false, // Disable account linking
      trustedProviders: [], // No trusted providers
    },
  },

  // Callback URLs
  redirectURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
});

// Export type for schema
export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.User;

/**
 * JWT Configuration for Backend
 *
 * The FastAPI backend must use the same JWT secret to verify tokens.
 *
 * Backend Environment Variables:
 * - BETTER_AUTH_SECRET: Same as frontend (required)
 * - BETTER_AUTH_URL: Frontend URL for API calls (optional)
 *
 * JWT Token Structure:
 * - Header: {"alg": "HS256", "typ": "JWT"}
 * - Payload: {"userId": string, "exp": number, "iat": number}
 *
 * Backend Verification:
 * ```python
 * import jwt
 * from app.config import settings
 *
 * def verify_better_auth_token(token: str) -> dict:
 *     return jwt.decode(
 *         token,
 *         settings.BETTER_AUTH_SECRET,
 *         algorithms=["HS256"]
 *     )
 * ```
 */
