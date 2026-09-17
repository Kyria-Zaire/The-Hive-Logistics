import { useEffect } from "react";
import { render, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ContactPage from "@/app/contact/page";

vi.mock("next/script", () => ({
  default: function ScriptStub({ onLoad }: { onLoad?: () => void }) {
    useEffect(() => {
      onLoad?.();
    }, [onLoad]);
    return null;
  },
}));

describe("ContactPage — validation anti-spam", () => {
  beforeEach(() => {
    vi.stubEnv("NEXT_PUBLIC_TURNSTILE_SITE_KEY", "1x00000000000000000000AA");
    // render() never calls back: no Turnstile token is issued.
    window.turnstile = { render: vi.fn(() => "widget-id"), reset: vi.fn(), remove: vi.fn() };
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    delete window.turnstile;
  });

  it.each([
    { formId: "contact", button: "Envoyer le message", errorId: "contact-turnstile-error" },
    { formId: "devis", button: "Envoyer la demande", errorId: "quote-turnstile-error" },
  ])(
    "formulaire $formId : sans jeton, l'erreur anti-spam s'affiche sous le widget et lui est rattachée",
    async ({ formId, button, errorId }) => {
      const user = userEvent.setup();
      const { container } = render(<ContactPage />);
      const formElement = container.querySelector<HTMLFormElement>(`form#${formId}`);
      if (!formElement) {
        throw new Error(`form#${formId} introuvable`);
      }
      const form = within(formElement);

      await user.click(form.getByRole("button", { name: button }));

      expect(form.getByText("Validation anti-spam requise.")).toHaveAttribute("id", errorId);
      expect(form.getByRole("group", { name: "Vérification anti-spam" })).toHaveAttribute(
        "aria-describedby",
        errorId,
      );
    },
  );
});
