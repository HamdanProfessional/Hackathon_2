import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

/**
 * Hook to protect authenticated routes
 *
 * This hook checks for the presence of a JWT token in localStorage
 * and redirects to the login page if no token is found.
 *
 * Usage:
 * ```typescript
 * function ProtectedPage() {
 *   useAuthGuard();
 *
 *   return <div>Protected content</div>;
 * }
 * ```
 */
export function useAuthGuard() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Skip auth check for public routes
    const publicRoutes = ["/", "/login", "/register"];
    const isPublicRoute = publicRoutes.includes(pathname);

    if (isPublicRoute) {
      return;
    }

    // Check for token in localStorage (check both keys for compatibility)
    const token = localStorage.getItem("access_token") || localStorage.getItem("todo_access_token");

    if (!token) {
      // Redirect to login page with return URL
      const loginUrl = `/login${pathname !== "/dashboard" ? `?returnTo=${encodeURIComponent(pathname)}` : ""}`;
      router.push(loginUrl);
      return;
    }

    // Optional: Validate token format (JWT has 3 parts separated by dots)
    const tokenParts = token.split(".");
    if (tokenParts.length !== 3) {
      console.error("Invalid token format");
      localStorage.removeItem("access_token");
      localStorage.removeItem("todo_access_token");
      router.push("/login");
      return;
    }

    // Optional: Check if token is expired (basic check)
    try {
      const payload = JSON.parse(atob(tokenParts[1]));
      const currentTime = Date.now() / 1000;

      if (payload.exp && payload.exp < currentTime) {
        console.log("Token expired");
        localStorage.removeItem("access_token");
        localStorage.removeItem("todo_access_token");
        router.push("/login");
        return;
      }
    } catch (error) {
      console.error("Error parsing token:", error);
      localStorage.removeItem("access_token");
      localStorage.removeItem("todo_access_token");
      router.push("/login");
      return;
    }
  }, [router, pathname]);
}

/**
 * Hook to handle login redirection with return URL
 *
 * After successful login, this hook will redirect the user
 * to the URL they were originally trying to access.
 */
export function useAuthRedirect() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check for return URL in query params or sessionStorage
    const urlParams = new URLSearchParams(window.location.search);
    const returnTo = urlParams.get("returnTo") || sessionStorage.getItem("returnTo");

    if (returnTo && returnTo !== pathname) {
      sessionStorage.removeItem("returnTo"); // Clean up
      router.push(returnTo);
    }
  }, [router, pathname]);
}