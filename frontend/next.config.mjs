/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  compress: true,
  poweredByHeader: false,
  output: 'standalone', // Enable standalone output for Docker deployment
  experimental: {
    optimizePackageImports: ['lucide-react']
  },
  // Override API URL for production
  env: {
    // Environment variable takes priority - Kubernetes/Docker can override at runtime
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }
};

export default nextConfig;
