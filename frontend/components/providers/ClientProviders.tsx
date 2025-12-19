"use client";

import { ThemeProvider } from "./ThemeProvider";
import { Toaster } from "@/components/ui/toaster";

export default function ClientProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="todo-app-theme" attribute="class">
      {children}
      <Toaster />
    </ThemeProvider>
  );
}
