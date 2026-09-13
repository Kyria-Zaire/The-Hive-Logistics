import { homeContent } from "@/lib/content/home";
import { HOME_ANCHORS, ROUTES } from "@/lib/routes";
import { CtaLink } from "@/components/ui/cta-link";
import { HeroMedia } from "@/components/home/hero-media";

export function HeroSection() {
  const { hero } = homeContent;

  return (
    <section
      aria-labelledby="hero-heading"
      className="relative flex min-h-[100svh] flex-col justify-end min-[1440px]:min-h-[92svh]"
    >
      <HeroMedia />
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(105deg,rgba(10,10,10,0.88)_0%,rgba(10,10,10,0.45)_45%,rgba(10,10,10,0.25)_100%)]" />
      <div className="thl-hero-content">
        <div className="thl-container">
          <div className="thl-hero-grid-bg thl-hero-block max-w-3xl rounded-sm thl-hero-reveal">
            <p className="thl-hero-eyebrow text-xs uppercase tracking-[0.08em] text-thl-text-muted md:text-[0.8125rem]">
              {hero.eyebrow}
            </p>
            <h1
              id="hero-heading"
              className="thl-hero-h1 thl-hero-title font-semibold text-thl-text-primary"
            >
              {hero.h1Before}
              <span className="thl-hero-serif-accent">{hero.h1Accent}</span>
              {hero.h1After}
            </h1>
            <p className="thl-hero-lede max-w-[520px] text-base leading-relaxed text-thl-text-secondary md:text-lg">
              {hero.paragraph}
            </p>
            <div className="thl-hero-actions flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
              <CtaLink href={ROUTES.quote} variant="primary">
                {hero.ctaPrimary}
              </CtaLink>
              <CtaLink href={HOME_ANCHORS.services} variant="outline">
                {hero.ctaSecondary}
              </CtaLink>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
