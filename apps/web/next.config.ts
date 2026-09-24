import type { NextConfig } from "next";

const apiOrigin = process.env.THL_API_DEV_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Any value outside this list is silently coerced to 75. 60 for the vision backdrop, which
  // stays under a veil; 80 for the engagements photograph, which ends its scroll at full bleed
  // and unveiled (TICKET 23-BIS).
  images: { qualities: [60, 75, 80] },
  /**
   * En-têtes de sécurité (TICKET 31-BIS). Posés ici et non côté Vercel pour que DEV, RECETTE
   * et PROD partagent la même politique : un en-tête qui n'existe qu'en production est un
   * en-tête qu'on découvre cassé en production.
   *
   * Absent volontairement : `Content-Security-Policy`. Une CSP stricte doit composer avec GSAP,
   * Turnstile et les scripts inline de Next (nonce ou strict-dynamic) — arbitré en ticket V3.1
   * dédié, voir TECH_DEBT dette 28. `Strict-Transport-Security` est injecté par Vercel et n'est
   * pas repris ici (dette 29).
   */
  async headers() {
    return [
      {
        // `/:path*` couvre aussi la racine : `path*` accepte zéro segment.
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
        ],
      },
    ];
  },
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
