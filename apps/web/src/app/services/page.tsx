import type { Metadata } from "next";
import Link from "next/link";
import { CtaLink } from "@/components/ui/cta-link";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { ServiceCard } from "@/components/home/service-card";
import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";

export const metadata: Metadata = {
  title: "Services",
  description:
    "Convoyage automobile, gestion de flotte et logistique premium.",
  alternates: { canonical: ROUTES.services },
};

export default function ServicesPage() {
  const { services, methodChapter } = homeContent;

  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
        <section aria-labelledby="services-page-heading" className="pt-32 pb-[var(--space-6)] lg:pt-[var(--space-7)]">
          <div className="thl-container">
            <p className="text-caption text-[var(--text-muted)]">{services.eyebrow}</p>
            <h1 id="services-page-heading" className="text-display-m mt-4 max-w-4xl">Convoyage et logistique premium</h1>
            <span aria-hidden className="mt-[var(--space-4)] block h-px w-16 bg-[var(--accent)]" />
            <p className="text-body-l mt-[var(--space-4)] max-w-2xl text-[var(--text-secondary)]">Une offre complète pour vos véhicules d&apos;exception.</p>
          </div>
        </section>

        <section aria-labelledby="services-list-heading" className="pb-[var(--space-6)]">
          <div className="thl-container">
            <h2 id="services-list-heading" className="sr-only">{services.title}</h2>
            <ul className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {services.items.map((item, index) => (
                <li
                  key={item.id}
                  className={
                    index === services.items.length - 1 ? "md:col-span-2 lg:col-span-1" : undefined
                  }
                >
                  <ServiceCard item={item} />
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* Condensed twin of the home timeline: same typographic scale, without its observer,
            its "Nos principes" block and the #methode-hive anchor, which must stay unique. */}
        <section aria-labelledby="method-link-heading" className="pb-[var(--space-6)] lg:pb-[var(--space-7)]">
          <div className="thl-container">
            <div className="border-t border-[var(--border)] pt-[var(--space-6)] lg:pt-[var(--space-7)]">
              <p className="text-caption text-[var(--text-muted)]">{methodChapter.eyebrow}</p>
              <h2 id="method-link-heading" className="text-display-m mt-4 text-[var(--text-primary)]">{methodChapter.chapterTitle}</h2>
              <ol className="mt-[var(--space-6)] flex flex-col gap-[var(--space-5)] border-l border-[var(--border)] pl-[var(--space-4)] lg:flex-row lg:gap-0 lg:border-l-0 lg:border-t lg:pl-0">
                {methodChapter.steps.map((step) => (
                  <li key={step.num} className="lg:flex-1 lg:pr-[var(--space-5)] lg:pt-[var(--space-5)] lg:last:pr-0">
                    <span className="text-display-l block font-normal text-[var(--accent)]">{step.num}</span>
                    <h3 className="text-heading mt-[var(--space-4)] text-[var(--text-primary)]">{step.title}</h3>
                    <p className="text-body mt-[var(--space-3)] text-[var(--text-secondary)]">{step.text}</p>
                  </li>
                ))}
              </ol>
              <p className="text-body mt-[var(--space-5)] max-w-2xl text-[var(--text-secondary)]">Découvrez notre méthode sur la page d&apos;accueil.</p>
              <Link className="thl-text-link thl-focus-dark mt-[var(--space-4)]" href="/#methode-hive">Voir notre méthode</Link>
            </div>
          </div>
        </section>

        <section aria-labelledby="services-cta-heading" className="bg-[var(--bg-secondary)] py-[var(--space-6)] lg:py-[var(--space-7)]">
          <div className="thl-container text-center">
            <h2 id="services-cta-heading" className="text-display-m">Un projet de convoyage ?</h2>
            <div className="mt-[var(--space-5)] flex flex-col justify-center gap-3 sm:flex-row">
              <CtaLink href={ROUTES.quote} variant="primary">Demander un devis</CtaLink>
              <CtaLink href={ROUTES.contact} variant="outline">Nous contacter</CtaLink>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
