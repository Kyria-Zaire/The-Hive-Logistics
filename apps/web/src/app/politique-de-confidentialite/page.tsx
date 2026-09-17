import type { Metadata } from "next";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { company, companyAddressLine } from "@/lib/content/company";
import { ROUTES } from "@/lib/routes";

export const metadata: Metadata = {
  title: "Politique de confidentialité",
  description: "Politique de confidentialité de THE HIVE LOGISTICS.",
  alternates: { canonical: ROUTES.legalPrivacy },
};

const sections = [
  ["Responsable du traitement", `${company.legalName}, ${companyAddressLine}.`],
  ["Données collectées", "Formulaire contact : nom, prénom, email, sujet, message ; téléphone et entreprise facultatifs. Demande de devis : nom, prénom, email, téléphone, service souhaité, villes et codes postaux de départ et d'arrivée, date ou période souhaitée, catégorie, marque et modèle du véhicule, caractère roulant ; entreprise, contraintes particulières, message complémentaire et préférence de contact facultatifs. Données techniques : date et heure de la demande, référence de la demande, version de la politique de confidentialité portée à votre connaissance, empreinte pseudonymisée de l'adresse IP à des fins de sécurité."],
  ["Finalité du traitement", "Vos données sont traitées pour : répondre à vos demandes de contact et de devis, assurer le suivi commercial, sécuriser les formulaires (protection anti-spam, limitation des abus), respecter nos obligations légales et comptables."],
  ["Base légale", "Mesures précontractuelles prises à votre demande (art. 6.1.b RGPD) pour le traitement des demandes de contact et de devis ; intérêt légitime (art. 6.1.f) pour la sécurité du site et le suivi commercial ; obligation légale (art. 6.1.c) pour les obligations comptables."],
  ["Durée de conservation", `Les données sont conservées ${company.dataRetention}.`],
  ["Destinataires", "The HIVE LOGISTICS et ses sous-traitants techniques, dans la stricte limite de leurs missions : Vercel Inc. (hébergement du site), Cloudflare, Inc. (protection anti-spam Turnstile), l'hébergeur de l'API et de la base de données, et le fournisseur d'email transactionnel. Certains sous-traitants sont établis aux États-Unis ; les transferts sont encadrés par les clauses contractuelles types de la Commission européenne."],
  ["Droits des personnes", `Vous pouvez exercer les droits d'accès, de rectification, d'effacement, de limitation, d'opposition et de portabilité selon les conditions applicables. Pour exercer ces droits : ${company.email}.`],
  ["Cookies", "Voir la section Cookies des mentions légales."],
  ["Exercice de vos droits", `Pour exercer vos droits (accès, rectification, effacement, limitation, opposition, portabilité), contactez : ${company.email}`],
  ["Réclamation CNIL", "En cas de désaccord, vous pouvez introduire une réclamation auprès de la CNIL — 3 place de Fontenoy – TSA 80715 – 75334 Paris Cedex 07 — www.cnil.fr"],
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