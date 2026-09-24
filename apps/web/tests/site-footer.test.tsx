import { render, screen } from "@testing-library/react";
import { SiteFooter } from "@/components/layout/site-footer";
import { company } from "@/lib/content/company";

describe("SiteFooter", () => {
  it("affiche l'adresse, le téléphone et l'email de l'éditeur", () => {
    render(<SiteFooter />);

    expect(screen.getByText("78 Rue Frédéric Passy, 51430 Bezannes")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "06 21 23 96 43" })).toHaveAttribute(
      "href",
      "tel:+33621239643",
    );
    expect(screen.getByRole("link", { name: "contact@thehivelogistics.fr" })).toHaveAttribute(
      "href",
      "mailto:contact@thehivelogistics.fr",
    );
    expect(screen.queryByText(/prochainement/i)).not.toBeInTheDocument();
  });

  it("lie le compte Instagram en nouvel onglet, sans fuite de référent", () => {
    render(<SiteFooter />);

    const instagram = screen.getByRole("link", { name: /^Instagram/ });

    expect(instagram).toHaveAttribute("href", company.social.instagram.url);
    expect(instagram).toHaveAttribute("target", "_blank");
    // noopener contre le détournement d'onglet, noreferrer contre la fuite de l'URL d'origine.
    expect(instagram).toHaveAttribute("rel", "noopener noreferrer");
    // Le nom accessible doit contenir le texte visible (WCAG 2.5.3).
    expect(instagram).toHaveAccessibleName(
      expect.stringContaining(company.social.instagram.handle),
    );
    expect(screen.getByText(company.social.instagram.handle)).toBeInTheDocument();
  });

  it("n'affiche aucun lien LinkedIn tant que son URL n'est pas fournie", () => {
    render(<SiteFooter />);

    expect(company.social.linkedin.url).toBe("");
    expect(screen.queryByRole("link", { name: /LinkedIn/i })).not.toBeInTheDocument();
  });
});
