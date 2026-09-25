import type { Metadata } from "next";
import { CtaLink } from "@/components/ui/cta-link";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { ServiceCard } from "@/components/home/service-card";
import { MethodChapterSection } from "@/components/home/method-chapter-section";
import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";

export const metadata: Metadata = {
  title: "Services",
  description:
    "Convoyage automobile, gestion de flotte et logistique automobile.",
  alternates: { canonical: ROUTES.services },
};

export default function ServicesPage() {
  const { services } = homeContent;

  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
        <section aria-labelledby="services-page-heading" className="pt-32 pb-[var(--space-6)] lg:pt-[var(--space-7)]">
          <div className="thl-container">
            <p className="text-caption text-[var(--text-muted)]">{services.eyebrow}</p>
            <h1 id="services-page-heading" className="text-display-m mt-4 max-w-4xl">Convoyage et logistique automobile</h1>
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
                  <ServiceCard item={item} wide={index === services.items.length - 1} />
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* The home chapter itself, road, car and pinned screens included — CTO call: this
            route carries GSAP too, and the section's own #methode-hive anchor now exists on
            both pages. The "Voir notre méthode" link that used to stand here went with it:
            it sent the visitor to the home for a chapter they were already reading. */}
        <MethodChapterSection />

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
