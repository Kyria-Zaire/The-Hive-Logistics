import type { NextConfig } from "next";

const apiOrigin = process.env.THL_API_DEV_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // 60 for the two full-bleed backgrounds: any value outside this list is coerced to 75.
  images: { qualities: [60, 75] },
  async rewrites() {
    if (process.env.NODE_ENV !== "development") {
      return [];
    }
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiOrigin}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
