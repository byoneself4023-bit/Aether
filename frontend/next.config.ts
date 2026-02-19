import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Enable if you need to proxy API calls during development
  // async rewrites() {
  //   return [
  //     { source: '/api/auth/:path*', destination: 'http://localhost:8003/api/auth/:path*' },
  //     { source: '/api/portfolio/:path*', destination: 'http://localhost:8001/api/:path*' },
  //     { source: '/api/llm/:path*', destination: 'http://localhost:8002/api/:path*' },
  //   ];
  // },
};

export default nextConfig;
