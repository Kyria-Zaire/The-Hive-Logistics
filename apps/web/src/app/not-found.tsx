import { CtaLink } from "@/components/ui/cta-link";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { ROUTES } from "@/lib/routes";

export default function NotFound() {
  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="flex min-h-screen flex-1 items-center bg-[var(--bg-primary)] py-32 text-[var(--text-primary)]">
        <div className="thl-container">
          <div className="max-w-2xl">
            <p className="text-caption text-[var(--text-muted)]">THE HIVE LOGISTICS</p>
            <h1 className="text-display-m mt-4">Page introuvable</h1>
            <p className="text-body-l mt-5 text-[var(--text-secondary)]">
              La page que vous cherchez n&apos;existe pas ou a été déplacée.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <CtaLink href={ROUTES.home} variant="primary">Retour à l&apos;accueil</CtaLink>
              <CtaLink href={ROUTES.contact} variant="outline">Nous contacter</CtaLink>
            </div>
          </div>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}