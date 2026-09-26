import { render, screen } from "@testing-library/react";
import HomePage from "@/app/page";
import {
  forbiddenPublicPhrases,
  homeContent,
} from "@/lib/content/home";
import { CAP_005_PORTFOLIO_ENABLED } from "@/lib/features";
import { ROUTES } from "@/lib/routes";

describe("HomePage", () => {
  it("rend la page d'accueil avec un seul h1", () => {
    render(<HomePage />);
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(
      screen.getByRole("heading", {
        level: 1,
        name: /THE HIVE LOGISTICS/i,
      }),
    ).toBeInTheDocument();
  });

  it("expose la navigation principale et le menu mobile", () => {
    render(<HomePage />);
    const homeLink = screen.getByRole("link", {
      name: homeContent.footer.wordmark,
    });
    expect(homeLink).toHaveAttribute("href", ROUTES.home);
    const logo = homeLink.querySelector('img[src*="logo.png"]');
    expect(logo).toHaveAttribute("alt", "");
    expect(logo).toHaveAttribute("aria-hidden", "true");
    expect(screen.getAllByRole("navigation", { name: homeContent.nav.primary }).length).toBeGreaterThanOrEqual(1);
    const menuButton = screen.getByRole("button", {
      name: homeContent.nav.menuOpen,
    });
    expect(menuButton).toHaveAttribute("aria-expanded", "false");
  });

  it("contient les CTA Hero et liens futurs", () => {
    render(<HomePage />);
    expect(
      screen.getAllByRole("link", { name: homeContent.hero.ctaPrimary }).length,
    ).toBeGreaterThan(0);
    expect(
      screen.getByRole("link", { name: homeContent.hero.ctaSecondary }),
    ).toHaveAttribute("href", ROUTES.services);
    const serviceLinks = screen.getAllByRole("link", { name: homeContent.nav.services });
    expect(serviceLinks.some((link) => link.getAttribute("href") === ROUTES.services)).toBe(
      true,
    );
  });

  it("n'affiche pas la section réalisations si CAP-005 inactive", () => {
    expect(CAP_005_PORTFOLIO_ENABLED).toBe(false);
    render(<HomePage />);
    expect(screen.queryByRole("heading", { name: /réalisations/i })).not.toBeInTheDocument();
  });

  it("n'expose qu'un seul CTA primaire rouge, dans le Hero", () => {
    const { container } = render(<HomePage />);
    const primaryRed = container.querySelectorAll('[data-thl-cta="primary-red"]');
    expect(primaryRed).toHaveLength(1);
    const hero = container.querySelector("#hero-heading")?.closest("section");
    expect(hero).toBeTruthy();
    expect(hero?.contains(primaryRed[0] ?? null)).toBe(true);
  });

  it("n'expose pas les services interdits dans le texte public", () => {
    render(<HomePage />);
    const main = screen.getByRole("main");
    const text = main.textContent ?? "";
    for (const phrase of forbiddenPublicPhrases) {
      expect(text.toLowerCase()).not.toContain(phrase);
    }
  });
});
