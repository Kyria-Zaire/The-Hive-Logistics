import type { Metadata } from "next";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
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
      "[À COMPLÉTER : dénomination sociale]",
      "[À COMPLÉTER : SIRET]",
      "[À COMPLÉTER : adresse du siège social]",
      "[À COMPLÉTER : nom du dirigeant]",
    ],
  },
  {
    title: "Hébergeur",
    paragraphs: ["[À COMPLÉTER : hébergeur (ex: Vercel Inc.)]"],
  },
  {
    title: "Propriété intellectuelle",
    paragraphs: [
      "Les éléments de ce site sont présentés sous réserve de la validation des droits et mentions applicables.",
      "[À COMPLÉTER : titulaire des droits et conditions d'utilisation des contenus]",
    ],
  },
  {
    title: "Responsabilité",
    paragraphs: [
      "[À COMPLÉTER : informations relatives à la responsabilité de l'éditeur]",
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
      "[À COMPLÉTER : politique applicable aux cookies et traceurs]",
    ],
  },
  {
    title: "Droit applicable",
    paragraphs: ["[À COMPLÉTER : droit applicable et juridiction compétente]"],
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