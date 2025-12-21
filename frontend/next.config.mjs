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
    NEXT_PUBLIC_API_URL: process.env.NODE_ENV === 'production'
      ? 'https://backend-m8qs0wvvo-hamdanprofessionals-projects.vercel.app'
      : 'http://localhost:8000'
  }
};

export default nextConfig;
