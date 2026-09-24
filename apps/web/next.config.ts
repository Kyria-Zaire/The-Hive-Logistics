import type { NextConfig } from "next";

const apiOrigin = process.env.THL_API_DEV_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Any value outside this list is silently coerced to 75. 60 for the vision backdrop, which
  // stays under a veil; 80 for the engagements photograph, which ends its scroll at full bleed
  // and unveiled (TICKET 23-BIS).
  images: { qualities: [60, 75, 80] },
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
