import Link from "next/link";
import { company, companyAddressLine } from "@/lib/content/company";
import { homeContent } from "@/lib/content/home";
import {
  SHOW_FOOTER_CONTACT_DETAILS,
  SHOW_FOOTER_SOCIAL_LINKS,
} from "@/lib/features";
import { SocialLinks } from "@/components/layout/social-links";
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
            {/* Attribution required by the footage licence: it belongs where anyone looking
                for it would look, under the copyright line. */}
            <p className="mt-2 text-xs text-thl-text-muted">{footer.mediaCredit}</p>
          </div>
          {SHOW_FOOTER_CONTACT_DETAILS ? (
            <div>
              <p className="text-sm font-medium text-thl-text-primary">Coordonnées</p>
              <address className="mt-4 flex flex-col gap-3 text-sm not-italic text-thl-text-secondary">
                <span>{companyAddressLine}</span>
                <a
                  href={`tel:${company.phone.e164}`}
                  className="thl-focus-dark hover:text-thl-text-primary"
                >
                  {company.phone.display}
                </a>
                <a
                  href={`mailto:${company.email}`}
                  className="thl-focus-dark hover:text-thl-text-primary"
                >
                  {company.email}
                </a>
              </address>
            </div>
          ) : null}
          {SHOW_FOOTER_SOCIAL_LINKS ? (
            <div>
              <p className="text-sm font-medium text-thl-text-primary">Réseaux sociaux</p>
              <SocialLinks
                className="mt-4"
                linkClassName="thl-focus-dark text-sm text-thl-text-secondary hover:text-thl-text-primary"
              />
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
