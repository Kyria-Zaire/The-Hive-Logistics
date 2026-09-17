import { render, screen } from "@testing-library/react";
import { SiteFooter } from "@/components/layout/site-footer";

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
});
