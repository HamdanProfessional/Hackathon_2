/**
 * Better Auth API Routes - DISABLED
 *
 * These routes are disabled because we use the FastAPI backend for authentication.
 * The Python backend handles all auth operations at /api/auth/login, /api/auth/register, etc.
 *
 * To enable Better Auth server-side auth in Next.js:
 * 1. Configure a database connection
 * 2. Uncomment the imports and export below
 * 3. Update the auth-instance.ts configuration
 */

// import { auth } from "@/lib/auth-instance";
// import { toNextJsHandler } from "better-auth/next-js";
// export const { GET, POST } = toNextJsHandler(auth);

// Temporarily return 404 to prevent these routes from being used
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ message: 'Use FastAPI backend for authentication' }, { status: 404 });
}

export async function POST() {
  return NextResponse.json({ message: 'Use FastAPI backend for authentication' }, { status: 404 });
}
