import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import ClientProviders from "@/components/providers/ClientProviders";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Evolution Todo - Modern Task Management",
  description: "A modern full-stack task management application with real-time search, filtering, and beautiful glassmorphism design",
  keywords: ["todo", "task management", "productivity", "organization", "search", "filter", "nextjs", "fastapi"],
  authors: [{ name: "PIAIC Hackathon Team" }],
  creator: "PIAIC Hackathon Team",
  publisher: "PIAIC",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "/",
    title: "Evolution Todo - Modern Task Management",
    description: "Organize your tasks with real-time search, filtering, and beautiful glassmorphism design",
    siteName: "Evolution Todo",
  },
  twitter: {
    card: "summary_large_image",
    title: "Evolution Todo - Modern Task Management",
    description: "Organize your tasks with real-time search, filtering, and beautiful glassmorphism design",
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ClientProviders>
          <div className="min-h-screen bg-background">
            {children}
          </div>
        </ClientProviders>
      </body>
    </html>
  );
}
