import type { Metadata } from "next";
import { CtaLink } from "@/components/ui/cta-link";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";

export const metadata: Metadata = {
  title: "À propos",
  description:
    "THE HIVE LOGISTICS, spécialiste du convoyage automobile premium, de la gestion de flotte et de la logistique haut de gamme.",
  alternates: { canonical: ROUTES.about },
};

export default function AboutPage() {
  const { engagements, vision } = homeContent;

  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
        <section aria-labelledby="about-heading" className="pt-32 pb-[var(--space-6)]">
          <div className="thl-container">
            <p className="text-caption text-[var(--text-muted)]">À PROPOS</p>
            <h1 id="about-heading" className="text-display-m mt-4">THE HIVE LOGISTICS</h1>
            <p className="text-body-l mt-5 max-w-2xl text-[var(--text-secondary)]">L&apos;exigence au service de la mobilité premium.</p>
          </div>
        </section>

        <section aria-labelledby="about-engagements-heading" className="bg-[var(--bg-secondary)] py-[var(--space-6)]">
          <div className="thl-container">
            <p className="text-caption text-[var(--text-muted)]">{engagements.eyebrow}</p>
            <h2 id="about-engagements-heading" className="text-display-m mt-4">{engagements.title}</h2>
            <ul className="mt-[var(--space-5)] grid grid-cols-1 gap-[var(--space-5)] lg:grid-cols-3">
              {engagements.items.map((item) => (
                <li key={item.title} className="border-l-2 border-[var(--accent)] pl-[var(--space-4)]">
                  <article>
                    <h3 className="text-heading">{item.title}</h3>
                    <p className="text-body mt-3 text-[var(--text-secondary)]">{item.description}</p>
                  </article>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section aria-labelledby="about-vision-heading" className="py-[var(--space-6)]">
          <div className="thl-container max-w-3xl text-center">
            <p className="text-caption text-[var(--text-muted)]">{vision.eyebrow}</p>
            <h2 id="about-vision-heading" className="text-display-m mt-4">{vision.title}</h2>
            <p className="text-body-l mt-6 text-[var(--text-secondary)]">{vision.body}</p>
          </div>
        </section>

        <section aria-labelledby="about-cta-heading" className="bg-[var(--bg-secondary)] py-[var(--space-6)]">
          <div className="thl-container text-center">
            <h2 id="about-cta-heading" className="text-display-m">Travaillons ensemble.</h2>
            <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <CtaLink href={ROUTES.contact} variant="primary">Nous contacter</CtaLink>
              <CtaLink href={ROUTES.services} variant="outline">Voir nos services</CtaLink>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}