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
          {/* max-w-5xl: the slogan needs ~970px to hold on one line at 56px. */}
          {/* The five blocks hold for 7.5s before entering, so the loop plays almost to its
              end — 8.68s — before the words arrive. The 150/200/100/100ms stagger between
              them is unchanged, only pushed back. Reduced motion skips the hold entirely:
              the rule below drops the animation and leaves everything opaque from the first
              paint. */}
          <div className="max-w-5xl">
            <p
              className="hero-enter thl-hero-eyebrow text-caption text-[var(--text-primary)]"
              style={
                {
                  "--enter-y": "20px",
                  "--enter-delay": "7500ms",
                  "--enter-duration": "800ms",
                } as React.CSSProperties
              }
            >
              CONVOYAGE AUTOMOBILE
            </p>
            <h1
              id="hero-heading"
              className="hero-enter text-display-xl mt-5 max-w-5xl font-semibold text-[var(--text-primary)]"
              style={
                {
                  "--enter-y": "30px",
                  "--enter-delay": "7650ms",
                  "--enter-duration": "900ms",
                } as React.CSSProperties
              }
            >
              THE HIVE LOGISTICS
            </h1>
            <p
              className="hero-enter thl-hero-lede text-display-m mt-6 max-w-5xl text-[var(--text-primary)]"
              style={
                {
                  "--enter-y": "20px",
                  "--enter-delay": "7850ms",
                  "--enter-duration": "800ms",
                } as React.CSSProperties
              }
            >
              Nous déplaçons plus que des véhicules.
            </p>
            {/* text-primary, not secondary: at 18px regular this line needs 4.5:1, and the
                grey measured 2.93:1 over the still and 3.31:1 over the video. White clears it
                everywhere. The hierarchy is carried by size and weight against the 56px lede
                above, so the line does not gain any prominence from the change. */}
            <p
              className="hero-enter text-body-l mt-[var(--space-3)] text-[var(--text-primary)]"
              style={
                {
                  "--enter-y": "20px",
                  "--enter-delay": "7950ms",
                  "--enter-duration": "700ms",
                } as React.CSSProperties
              }
            >
              Tous types de véhicules
            </p>
            <div
              className="hero-enter mt-10 flex w-full flex-col gap-3 sm:flex-row sm:items-center"
              style={
                {
                  "--enter-y": "20px",
                  "--enter-delay": "8050ms",
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
    </section>
  );
}
