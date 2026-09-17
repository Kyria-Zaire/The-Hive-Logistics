import { expect, test } from "@playwright/test";

/**
 * Real end-to-end check: production web build → Server Action → FastAPI → PostgreSQL → worker → Mailpit.
 * Requires the local DEV stack (see docs/demo/README.md), so it is skipped unless THL_E2E_REAL=1.
 * Uses fictitious data only (DEV: no real personal data).
 */
const realStackEnabled = process.env.THL_E2E_REAL === "1";
const webBaseUrl = process.env.THL_E2E_WEB_URL ?? "http://127.0.0.1:3100";
const mailpitBaseUrl = process.env.THL_E2E_MAILPIT_URL ?? "http://127.0.0.1:8025";

type MailpitSearchResponse = {
  messages_count: number;
  messages: { Subject: string }[];
};

test.describe("Contact — widget Turnstile après navigation client", { tag: "@e2e-ui" }, () => {
  // Only checks that the widget is rendered: no Turnstile challenge is solved, so no backend is needed.
  test("le widget est rendu dans les deux formulaires après un aller-retour / → /contact", async ({ page }) => {
    const nav = page.locator('header nav[aria-label="Navigation principale"]');
    const widgetInputs = () => [
      page.locator('form#contact input[name="cf-turnstile-response"]'),
      page.locator('form#devis input[name="cf-turnstile-response"]'),
    ];

    await page.goto("/contact");
    for (const input of widgetInputs()) {
      await expect(input).toBeAttached({ timeout: 20_000 });
    }

    // Marker survives only if the document is not reloaded (true client-side navigation).
    await page.evaluate(() => {
      (window as Window & { __thlSameDocument?: boolean }).__thlSameDocument = true;
    });
    await nav.getByRole("link", { name: "Accueil" }).click();
    await page.waitForURL("**/");
    await nav.getByRole("link", { name: "Contact" }).click();
    await page.waitForURL("**/contact");

    expect(
      await page.evaluate(() => (window as Window & { __thlSameDocument?: boolean }).__thlSameDocument),
    ).toBe(true);
    for (const input of widgetInputs()) {
      await expect(input).toBeAttached({ timeout: 20_000 });
    }
  });
});

test.describe("Contact — soumission réelle front + API", { tag: "@e2e-real" }, () => {
  test.skip(!realStackEnabled, "Stack locale réelle requise (API, PostgreSQL, worker, Mailpit) : THL_E2E_REAL=1");

  test("un message de contact est accepté, persisté puis notifié", async ({ page, request }) => {
    const marker = `e2e${Date.now()}`;

    await page.goto(`${webBaseUrl}/contact`);
    const form = page.locator("form#contact");
    await form.locator("#first_name").fill("Démo");
    await form.locator("#last_name").fill("Client");
    await form.locator("#email").fill(`demo+${marker}@example.com`);
    await form.locator("#subject").selectOption("information");
    await form.locator("#message").fill(`Test de démonstration ${marker}`);
    await form.locator('input[name="privacy_acknowledgement"]').check();

    const turnstileResponse = form.locator('input[name="cf-turnstile-response"]');
    await expect.poll(() => turnstileResponse.inputValue(), { timeout: 20_000 }).not.toBe("");

    await form.getByRole("button", { name: "Envoyer le message" }).click();
    await expect(form.getByRole("status")).toHaveText("Votre message a bien été transmis.", {
      timeout: 20_000,
    });

    // The notification job is inserted in the same transaction as the lead: an email carrying
    // the unique marker proves persistence and the worker → SMTP pipeline.
    await expect
      .poll(
        async () => {
          const response = await request.get(
            `${mailpitBaseUrl}/api/v1/search?query=${encodeURIComponent(marker)}`,
          );
          const body = (await response.json()) as MailpitSearchResponse;
          return body.messages.map((message) => message.Subject);
        },
        { timeout: 30_000 },
      )
      .toEqual([expect.stringMatching(/^\[THL\] Nouveau message de contact — THL-\d{8}-[0-9A-Z]{8}$/)]);
  });
});
