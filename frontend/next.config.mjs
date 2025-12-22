/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  compress: true,
  poweredByHeader: false,
  experimental: {
    optimizePackageImports: ['lucide-react']
  },
  // Override API URL for production
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production'
      ? 'https://backend-k4t2o36f2-hamdanprofessionals-projects.vercel.app'
      : 'http://localhost:8000')
  }
};

export default nextConfig;
