"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Dashboard error:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md border-destructive/50">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mb-4">
            <AlertTriangle className="h-8 w-8 text-destructive" />
          </div>
          <CardTitle className="text-2xl">Something went wrong!</CardTitle>
          <CardDescription>
            We encountered an error while loading your dashboard. Please try again or contact support if the problem persists.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-muted/50 p-3 rounded-md">
            <p className="text-sm text-muted-foreground">
              Error: {error.message || "Unknown error"}
            </p>
            {process.env.NODE_ENV === "development" && (
              <details className="mt-2">
                <summary className="text-xs cursor-pointer">Stack trace</summary>
                <pre className="mt-2 text-xs text-destructive whitespace-pre-wrap">
                  {error.stack}
                </pre>
              </details>
            )}
          </div>
          <div className="flex gap-2">
            <Button onClick={reset} className="flex-1">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try again
            </Button>
            <Button
              variant="outline"
              onClick={() => (window.location.href = "/")}
              className="flex-1"
            >
              Go home
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}