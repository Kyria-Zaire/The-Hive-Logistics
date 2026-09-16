"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowUpRight, Menu } from "lucide-react";
import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";
import { CtaLink } from "@/components/ui/cta-link";
import { MainNavLinks } from "@/components/navigation/main-nav-links";
import { MobileDrawer } from "@/components/navigation/mobile-drawer";

export function SiteHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 48);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const closeMenu = useCallback(() => {
    setMenuOpen(false);
  }, []);

  return (
    <>
      <header
        className={`fixed inset-x-0 top-0 z-40 border-b backdrop-blur-sm transition-[background-color,border-color] duration-[250ms] ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none ${
          scrolled
            ? "border-thl-border bg-thl-bg-anthracite"
            : "border-thl-border bg-thl-bg-deep/80"
        }`}
      >
        <div className="thl-container flex h-16 items-center justify-between gap-4 md:h-[72px]">
          <Link
            href={ROUTES.home}
            className="text-sm font-semibold tracking-[0.12em] thl-focus-dark xl:text-base"
          >
            {homeContent.footer.wordmark}
          </Link>

          <nav
            className="hidden flex-1 justify-center lg:flex"
            aria-label={homeContent.nav.primary}
          >
            <MainNavLinks
              linkClassName="thl-focus-dark text-sm font-medium text-thl-text-secondary transition-colors hover:text-thl-text-primary"
            />
          </nav>

          <div className="flex items-center gap-2">
            <CtaLink
              href={ROUTES.quote}
              variant="header-compact"
              className="lg:inline-flex"
              icon={
                <ArrowUpRight size={16} strokeWidth={1.75} aria-hidden="true" />
              }
            >
              {homeContent.nav.quote}
            </CtaLink>
            <button
              ref={menuButtonRef}
              type="button"
              className="inline-flex size-11 items-center justify-center lg:hidden thl-focus-dark"
              aria-expanded={menuOpen}
              aria-controls="mobile-primary-nav"
              aria-label={
                menuOpen ? homeContent.nav.menuClose : homeContent.nav.menuOpen
              }
              onClick={() => setMenuOpen((value) => !value)}
            >
              <Menu size={22} aria-hidden="true" />
            </button>
          </div>
        </div>
      </header>
      <MobileDrawer
        open={menuOpen}
        onClose={closeMenu}
        menuButtonRef={menuButtonRef}
      />
    </>
  );
}
