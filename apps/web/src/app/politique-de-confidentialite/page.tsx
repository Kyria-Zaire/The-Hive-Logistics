import type { Metadata } from "next";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { ROUTES } from "@/lib/routes";

export const metadata: Metadata = {
  title: "Politique de confidentialité",
  description: "Politique de confidentialité de THE HIVE LOGISTICS.",
  alternates: { canonical: ROUTES.legalPrivacy },
};

const sections = [
  ["Responsable du traitement", "[À COMPLÉTER : identité et coordonnées du responsable du traitement]"],
  ["Données collectées", "Les formulaires Contact et Devis peuvent recueillir les champs nécessaires à l'instruction d'une demande. [À COMPLÉTER : liste validée des données et caractère obligatoire]"],
  ["Finalité du traitement", "[À COMPLÉTER : finalités précises du traitement des demandes]"],
  ["Base légale", "[À COMPLÉTER : base légale applicable à chaque finalité]"],
  ["Durée de conservation", "[À COMPLÉTER : durées de conservation validées]"],
  ["Destinataires", "[À COMPLÉTER : destinataires et sous-traitants autorisés]"],
  ["Droits des personnes", "Vous pouvez exercer les droits d'accès, de rectification, d'effacement, de limitation, d'opposition et de portabilité selon les conditions applicables. [À COMPLÉTER : modalités et coordonnées d'exercice]"],
  ["Cookies", "[À COMPLÉTER : cookies et traceurs utilisés, finalités et durée]"],
  ["Contact DPO", "[À COMPLÉTER : coordonnées du DPO ou point de contact dédié]"],
  ["Réclamation CNIL", "[À COMPLÉTER : informations validées relatives au droit de réclamation auprès de la CNIL]"],
] as const;

export default function PrivacyPolicyPage() {
  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="min-h-screen bg-[var(--bg-primary)] py-32 text-[var(--text-primary)]">
        <article className="thl-container max-w-4xl">
          <header className="max-w-3xl">
            <p className="text-caption text-[var(--text-muted)]">INFORMATIONS</p>
            <h1 className="text-display-m mt-4">Politique de confidentialité</h1>
          </header>
          <div className="mt-[var(--space-6)] max-w-3xl space-y-[var(--space-5)]">
            {sections.map(([title, text]) => (
              <section key={title} aria-labelledby={`privacy-${title}`}>
                <h2 id={`privacy-${title}`} className="text-heading">{title}</h2>
                <p className="text-body mt-4 text-[var(--text-secondary)]">{text}</p>
              </section>
            ))}
          </div>
        </article>
      </main>
      <SiteFooter />
    </>
  );
}