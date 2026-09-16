import type { Metadata } from "next";
import Link from "next/link";
import { CtaLink } from "@/components/ui/cta-link";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { ServiceIcon } from "@/components/home/service-icon";
import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";

export const metadata: Metadata = {
  title: "Services",
  description:
    "Convoyage automobile, gestion de flotte, logistique premium et préparation automobile.",
  alternates: { canonical: ROUTES.services },
};

export default function ServicesPage() {
  const { services, methodChapter } = homeContent;

  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
        <section aria-labelledby="services-page-heading" className="pt-32 pb-[var(--space-6)]">
          <div className="thl-container">
            <p className="text-caption text-[var(--text-muted)]">{services.eyebrow}</p>
            <h1 id="services-page-heading" className="text-display-m mt-4 max-w-4xl">Convoyage et logistique premium</h1>
            <p className="text-body-l mt-5 max-w-2xl text-[var(--text-secondary)]">Une offre complète pour vos véhicules d&apos;exception.</p>
          </div>
        </section>

        <section aria-labelledby="services-list-heading" className="pb-[var(--space-6)]">
          <div className="thl-container">
            <h2 id="services-list-heading" className="sr-only">{services.title}</h2>
            <ul className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-2">
              {services.items.map((item) => (
                <li key={item.id}>
                  <article className="flex min-h-64 flex-col border border-[var(--border)] bg-[var(--bg-elevated)] p-[var(--space-4)]">
                    <div className="text-[var(--accent)]"><ServiceIcon name={item.icon} /></div>
                    <h3 className="text-heading mt-[var(--space-5)]">{item.title}</h3>
                    <p className="text-body mt-[var(--space-3)] text-[var(--text-secondary)]">{item.description}</p>
                  </article>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section aria-labelledby="method-link-heading" className="bg-[var(--bg-secondary)] py-[var(--space-6)]">
          <div className="thl-container max-w-4xl">
            <p className="text-caption text-[var(--text-muted)]">{methodChapter.eyebrow}</p>
            <h2 id="method-link-heading" className="text-heading mt-4">{methodChapter.chapterTitle}</h2>
            <p className="text-body mt-4 text-[var(--text-secondary)]">Découvrez notre méthode sur la page d&apos;accueil.</p>
            <Link className="thl-text-link thl-focus-dark mt-6" href="/#methode-hive">Voir notre méthode</Link>
          </div>
        </section>

        <section aria-labelledby="services-cta-heading" className="py-[var(--space-6)]">
          <div className="thl-container text-center">
            <h2 id="services-cta-heading" className="text-display-m">Un projet de convoyage ?</h2>
            <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
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