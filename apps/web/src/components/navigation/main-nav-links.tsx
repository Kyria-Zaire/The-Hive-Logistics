import Link from "next/link";
import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";

const links = [
  { href: ROUTES.home, label: homeContent.nav.home },
  { href: ROUTES.services, label: homeContent.nav.services },
  { href: ROUTES.about, label: homeContent.nav.about },
  { href: ROUTES.contact, label: homeContent.nav.contact },
] as const;

type MainNavLinksProps = {
  id?: string;
  className?: string;
  onNavigate?: () => void;
  linkClassName?: string;
};

export function MainNavLinks({
  id,
  className = "",
  onNavigate,
  linkClassName = "thl-focus-dark block py-3 text-base text-thl-text-primary xl:inline-block xl:py-0 xl:text-sm xl:font-medium xl:text-thl-text-secondary xl:hover:text-thl-text-primary",
}: MainNavLinksProps) {
  return (
    <ul id={id} className={`flex flex-col gap-1 xl:flex-row xl:items-center xl:gap-8 ${className}`}>
      {links.map((item) => (
        <li key={item.href}>
          <Link href={item.href} className={linkClassName} onClick={onNavigate}>
            {item.label}
          </Link>
        </li>
      ))}
      <li className="mt-4 border-t border-thl-border pt-4 xl:hidden">
        <Link
          href={ROUTES.quote}
          className="thl-btn-outline thl-focus-dark w-full justify-center"
          onClick={onNavigate}
        >
          {homeContent.nav.quote}
        </Link>
      </li>
    </ul>
  );
}
