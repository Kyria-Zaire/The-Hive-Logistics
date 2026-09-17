import type { Metadata } from "next";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { company, companyAddressLine } from "@/lib/content/company";
import { ROUTES } from "@/lib/routes";

export const metadata: Metadata = {
  title: "Mentions légales",
  description: "Mentions légales de THE HIVE LOGISTICS.",
  alternates: { canonical: ROUTES.legalMentions },
};

const sections = [
  {
    title: "Éditeur du site",
    paragraphs: [
      `${company.legalName}, ${company.legalForm} au capital de ${company.shareCapital}`,
      `Immatriculation : ${company.registration}`,
      `TVA intracommunautaire : ${company.vatId}`,
      `Siège social : ${companyAddressLine}`,
      `Président : ${company.president}`,
      `Contact : ${company.email} — ${company.phone.display}`,
    ],
  },
  {
    title: "Hébergeur",
    paragraphs: [company.host],
  },
  {
    title: "Propriété intellectuelle",
    paragraphs: [
      "L'ensemble des éléments composant ce site (structure, textes, images, logos, vidéos) est la propriété exclusive de The HIVE LOGISTICS ou de ses partenaires, sauf mention contraire. Toute reproduction, représentation, modification ou exploitation, totale ou partielle, est interdite sans autorisation écrite préalable.",
    ],
  },
  {
    title: "Responsabilité",
    paragraphs: [
      "The HIVE LOGISTICS s'efforce d'assurer l'exactitude des informations diffusées sur ce site. Elle ne peut toutefois garantir l'absence d'erreur ou l'exhaustivité des contenus, et décline toute responsabilité pour tout dommage résultant de l'utilisation du site.",
    ],
  },
  {
    title: "Données personnelles",
    paragraphs: [
      <>Les informations relatives aux données personnelles sont présentées dans la <a className="underline" href={ROUTES.legalPrivacy}>politique de confidentialité</a>.</>,
    ],
  },
  {
    title: "Cookies",
    paragraphs: [
      "Ce site n'utilise aucun cookie publicitaire ou de traçage comportemental. Seuls des cookies strictement nécessaires au fonctionnement du site (protection anti-spam Cloudflare Turnstile) peuvent être déposés.",
    ],
  },
  {
    title: "Droit applicable",
    paragraphs: [
      "Le présent site est soumis au droit français. En cas de litige, et à défaut de résolution amiable, les tribunaux français seront compétents dans les conditions prévues par le Code de la consommation pour les particuliers, et par le Code de commerce pour les professionnels.",
    ],
  },
] as const;

export default function LegalNoticePage() {
  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="min-h-screen bg-[var(--bg-primary)] py-32 text-[var(--text-primary)]">
        <article className="thl-container max-w-4xl">
          <header className="max-w-3xl">
            <p className="text-caption text-[var(--text-muted)]">INFORMATIONS</p>
            <h1 className="text-display-m mt-4">Mentions légales</h1>
          </header>
          <div className="mt-[var(--space-6)] max-w-3xl space-y-[var(--space-5)]">
            {sections.map((section) => (
              <section key={section.title} aria-labelledby={`legal-${section.title}`}>
                <h2 id={`legal-${section.title}`} className="text-heading">{section.title}</h2>
                <div className="text-body mt-4 space-y-3 text-[var(--text-secondary)]">
                  {section.paragraphs.map((paragraph, index) => <p key={`${section.title}-${index}`}>{paragraph}</p>)}
                </div>
              </section>
            ))}
          </div>
        </article>
      </main>
      <SiteFooter />
    </>
  );
}