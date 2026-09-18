"use client";

import { ROUTES } from "@/lib/routes";
import { CtaLink } from "@/components/ui/cta-link";
import { HeroMedia } from "@/components/home/hero-media";

export function HeroSection() {
  return (
    <section
      aria-labelledby="hero-heading"
      className="relative flex min-h-screen flex-col justify-center overflow-hidden"
    >
      <HeroMedia />
      {/* Left scrim for the text column, light-to-dark vertical fade, then a light global veil. */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "linear-gradient(90deg, rgba(10,10,10,0.75) 0%, rgba(10,10,10,0) 65%), linear-gradient(180deg, rgba(10,10,10,0.1) 0%, rgba(10,10,10,0.28) 50%, rgba(10,10,10,0.92) 100%), rgba(10,10,10,0.37)",
        }}
      />
      <div className="relative z-10 w-full px-5 pt-24 md:px-8 lg:px-16">
        <div className="mx-auto w-full max-w-[1440px]">
          <div className="max-w-4xl">
            <p
              className="hero-enter thl-hero-eyebrow text-caption text-[var(--text-primary)]"
              style={
                {
                  "--enter-y": "20px",
                  "--enter-delay": "0ms",
                  "--enter-duration": "800ms",
                } as React.CSSProperties
              }
            >
              CONVOYAGE AUTOMOBILE PREMIUM
            </p>
            <h1
              id="hero-heading"
              className="hero-enter text-display-xl mt-5 max-w-5xl font-semibold text-[var(--text-primary)]"
              style={
                {
                  "--enter-y": "30px",
                  "--enter-delay": "150ms",
                  "--enter-duration": "900ms",
                } as React.CSSProperties
              }
            >
              THE HIVE LOGISTICS
            </h1>
            <p
              className="hero-enter thl-hero-lede text-display-m mt-6 max-w-3xl text-[var(--text-primary)]"
              style={
                {
                  "--enter-y": "20px",
                  "--enter-delay": "350ms",
                  "--enter-duration": "800ms",
                } as React.CSSProperties
              }
            >
              Nous déplaçons plus que des véhicules.
            </p>
            <div
              className="hero-enter mt-10 flex w-full flex-col gap-3 sm:flex-row sm:items-center"
              style={
                {
                  "--enter-y": "20px",
                  "--enter-delay": "550ms",
                  "--enter-duration": "700ms",
                } as React.CSSProperties
              }
            >
              <CtaLink href={ROUTES.quote} variant="primary" className="w-full sm:w-auto">
                Réserver un convoyage
              </CtaLink>
              <CtaLink href={ROUTES.services} variant="outline" className="w-full sm:w-auto">
                Découvrir nos services
              </CtaLink>
            </div>
          </div>
        </div>
      </div>
      <style jsx global>{`
        @keyframes thl-hero-enter {
          from {
            opacity: 0;
            transform: translateY(var(--enter-y, 20px));
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .hero-enter {
          opacity: 0;
          animation: thl-hero-enter var(--enter-duration, 800ms)
            var(--ease-lux) forwards;
          animation-delay: var(--enter-delay, 0ms);
        }

        @media (prefers-reduced-motion: reduce) {
          .hero-enter {
            animation: none;
            opacity: 1;
            transform: none;
          }
        }
      `}</style>
    </section>
  );
}
