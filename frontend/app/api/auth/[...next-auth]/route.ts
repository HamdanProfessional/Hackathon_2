/**
 * Better Auth API Routes
 *
 * These Next.js API routes handle authentication requests.
 * They bridge between Better Auth and our FastAPI backend.
 */

import { auth } from "@/lib/auth-instance";
import { toNextJsHandler } from "better-auth/next-js";

/**
 * Export all Better Auth routes as Next.js API handlers
 *
 * These routes are automatically available at:
 * - POST /api/auth/sign-in
 * - POST /api/auth/sign-up
 * - POST /api/auth/sign-out
 * - GET /api/auth/session
 * - POST /api/auth/reset-password
 *
 * Example usage in frontend:
 * ```typescript
 * import { authClient } from "@/lib/auth-client";
 *
 * // Sign in
 * await authClient.signIn.email({ email, password });
 *
 * // Get session
 * const session = await authClient.getSession();
 * ```
 */
export const { GET, POST } = toNextJsHandler(auth);
