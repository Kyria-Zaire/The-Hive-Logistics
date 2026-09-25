"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
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
  linkClassName = "thl-focus-dark block py-3 text-base uppercase tracking-[0.08em] text-thl-text-primary lg:inline-block lg:py-0 lg:text-sm lg:font-medium lg:text-thl-text-secondary lg:hover:text-thl-text-primary",
}: MainNavLinksProps) {
  const pathname = usePathname();

  return (
    <ul id={id} className={`flex flex-col gap-1 lg:flex-row lg:items-center lg:gap-8 ${className}`}>
      {links.map((item) => (
        <li key={item.href}>
          <Link
            href={item.href}
            className={linkClassName}
            onClick={onNavigate}
            aria-current={pathname === item.href ? "page" : undefined}
          >
            {item.label}
          </Link>
        </li>
      ))}
      <li className="mt-4 border-t border-thl-border pt-4 lg:hidden">
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
