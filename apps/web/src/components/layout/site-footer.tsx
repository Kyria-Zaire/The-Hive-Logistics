import Link from "next/link";
import { homeContent } from "@/lib/content/home";
import {
  SHOW_FOOTER_CONTACT_DETAILS,
  SHOW_FOOTER_SOCIAL_LINKS,
} from "@/lib/features";
import { ROUTES } from "@/lib/routes";

export function SiteFooter() {
  const year = new Date().getFullYear();
  const { footer } = homeContent;

  return (
    <footer className="border-t border-thl-border bg-thl-bg-anthracite py-12 md:py-16">
      <div className="thl-container">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-2 xl:grid-cols-3">
          <div>
            <p className="text-sm font-semibold tracking-[0.12em]">{footer.wordmark}</p>
            <p className="mt-4 text-sm text-thl-text-muted">
              © {year} {footer.wordmark}
            </p>
          </div>
          {SHOW_FOOTER_CONTACT_DETAILS ? (
            <div>
              <p className="text-sm font-medium text-thl-text-primary">Coordonnées</p>
              <p className="mt-4 text-sm text-thl-text-muted">
                Coordonnées disponibles prochainement.
              </p>
            </div>
          ) : null}
          {SHOW_FOOTER_SOCIAL_LINKS ? (
            <div>
              <p className="text-sm font-medium text-thl-text-primary">Réseaux sociaux</p>
              <p className="mt-4 text-sm text-thl-text-muted">
                Réseaux sociaux disponibles prochainement.
              </p>
            </div>
          ) : null}
          <nav aria-label="Liens du pied de page">
            <ul className="flex flex-col gap-3 text-sm">
              <li>
                <Link href={ROUTES.services} className="thl-focus-dark text-thl-text-secondary hover:text-thl-text-primary">
                  {footer.nav.services}
                </Link>
              </li>
              <li>
                <Link href={ROUTES.about} className="thl-focus-dark text-thl-text-secondary hover:text-thl-text-primary">
                  {footer.nav.about}
                </Link>
              </li>
              <li>
                <Link href={ROUTES.contact} className="thl-focus-dark text-thl-text-secondary hover:text-thl-text-primary">
                  {footer.nav.contact}
                </Link>
              </li>
              <li>
                <Link href={ROUTES.quote} className="thl-focus-dark text-thl-text-secondary hover:text-thl-text-primary">
                  {footer.nav.quote}
                </Link>
              </li>
            </ul>
          </nav>
          <nav aria-label="Informations légales">
            <ul className="flex flex-col gap-3 text-sm">
              <li>
                <Link
                  href={ROUTES.legalMentions}
                  className="thl-focus-dark text-thl-text-secondary hover:text-thl-text-primary"
                >
                  {footer.legal.mentions}
                </Link>
              </li>
              <li>
                <Link
                  href={ROUTES.legalPrivacy}
                  className="thl-focus-dark text-thl-text-secondary hover:text-thl-text-primary"
                >
                  {footer.legal.privacy}
                </Link>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </footer>
  );
}
