import type { Metadata } from "next";
import { CtaLink } from "@/components/ui/cta-link";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { EngagementsSection } from "@/components/home/engagements-section";
import { VisionSection } from "@/components/home/vision-section";
import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";

export const metadata: Metadata = {
  title: "À propos",
  description:
    "THE HIVE LOGISTICS, spécialiste du convoyage automobile, de la gestion de flotte et de la logistique automobile.",
  alternates: { canonical: ROUTES.about },
};

export default function AboutPage() {
  const { brandStatement } = homeContent;

  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
        <section aria-labelledby="about-heading" className="pt-32 pb-[var(--space-6)] lg:pt-[var(--space-7)]">
          <div className="thl-container">
            <h1 id="about-heading" className="text-display-m">À propos</h1>
            <p className="text-section-subtitle mt-4">THE HIVE LOGISTICS</p>
            <span aria-hidden className="mt-[var(--space-4)] block h-px w-16 bg-[var(--accent)]" />
            <p className="text-body-l mt-[var(--space-4)] max-w-2xl text-[var(--text-secondary)]">L&apos;exigence au service de la mobilité automobile.</p>
          </div>
        </section>

        {/* Narrative intro built from validated copy only: the home teases it with
            "Découvrir notre approche", this page carries it. No invented brand story. */}
        <section aria-labelledby="about-statement-heading" className="pb-[var(--space-6)] lg:pb-[var(--space-7)]">
          <div className="thl-container">
            <div className="max-w-3xl border-t border-[var(--border)] pt-[var(--space-6)] lg:pt-[var(--space-7)]">
              <h2 id="about-statement-heading" className="text-display-m text-[var(--text-primary)]">
                {brandStatement.title}
              </h2>
              <p className="text-body-l mt-[var(--space-4)] text-[var(--text-secondary)]">
                {brandStatement.body}
              </p>
            </div>
          </div>
        </section>

        {/* Les deux mêmes chapitres que l'accueil. Engagements importe son animation en dur,
            c'est donc lui qui amène GSAP sur cette route ; la Vision, depuis le TICKET 34,
            n'a plus d'animation à injecter. */}
        <EngagementsSection />

        <VisionSection showFolders />

        <section aria-labelledby="about-cta-heading" className="bg-[var(--bg-secondary)] py-[var(--space-6)] lg:py-[var(--space-7)]">
          <div className="thl-container text-center">
            <h2 id="about-cta-heading" className="text-display-m">Travaillons ensemble.</h2>
            <div className="mt-[var(--space-5)] flex flex-col justify-center gap-3 sm:flex-row">
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
