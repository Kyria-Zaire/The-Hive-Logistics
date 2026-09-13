import Link from "next/link";
import { homeContent } from "@/lib/content/home";
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
              <li>
                <Link
                  href={ROUTES.legalCookies}
                  className="thl-focus-dark text-thl-text-secondary hover:text-thl-text-primary"
                >
                  {footer.legal.cookies}
                </Link>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </footer>
  );
}
