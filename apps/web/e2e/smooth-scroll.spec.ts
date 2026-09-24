import { expect, test } from "@playwright/test";

/**
 * TICKET 19 — the four guard-rails attached to Lenis: it must stay off under reduced
 * motion, must not break the two in-page anchors, and must not break keyboard travel.
 * Lenis marks the root element with `lenis`/`lenis-smooth`, which is what we assert on.
 */

const isSmoothScrollActive = (page: import("@playwright/test").Page) =>
  page.evaluate(() => document.documentElement.classList.contains("lenis"));

test.describe("Défilement fluide — garde-fous", () => {
  test("Lenis est actif en mouvement normal @e2e-ui", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.goto("/");
    await expect.poll(() => isSmoothScrollActive(page)).toBe(true);
  });

  test("Lenis reste désactivé en mouvement réduit @e2e-ui", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/");
    await page.waitForTimeout(1000);
    expect(await isSmoothScrollActive(page)).toBe(false);

    // Native scrolling still works.
    await page.evaluate(() => window.scrollTo(0, 600));
    await page.waitForTimeout(300);
    expect(await page.evaluate(() => window.scrollY)).toBeGreaterThan(400);
  });

  // Reached by deep link rather than by clicking a link on another page: /services used to
  // carry one, and lost it when the method chapter itself moved onto that page. What the
  // guard-rail is actually about survives the change — Lenis owns anchor navigation, and the
  // target has to land below the fixed header rather than under it.
  test("l'ancre #methode-hive amène bien la section à l'écran @e2e-ui", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.goto("/#methode-hive");
    await expect.poll(() => isSmoothScrollActive(page)).toBe(true);

    const heading = page.locator("#methode-hive");
    await expect(heading).toBeInViewport({ timeout: 10_000 });

    // scroll-margin-top: 88px — the heading must clear the fixed header, not hide behind it.
    const header = page.locator("header").first();
    const gap = await heading.evaluate((el, headerHeight: number) => {
      return Math.round(el.getBoundingClientRect().top - headerHeight);
    }, (await header.boundingBox())?.height ?? 0);
    expect(gap).toBeGreaterThanOrEqual(0);
  });

  test("l'ancre #contenu-principal du skip-link fonctionne au clavier @e2e-ui", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.goto("/");
    await page.keyboard.press("Tab");

    const skip = page.locator(".thl-skip-link");
    await expect(skip).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/#contenu-principal$/);
    await expect(page.locator("#contenu-principal")).toBeAttached();
  });

  test("la navigation clavier amène l'élément focalisé dans le viewport @e2e-ui", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.goto("/");
    await expect.poll(() => isSmoothScrollActive(page)).toBe(true);

    // Walk until focus has actually had to scroll the page, rather than a fixed number of
    // presses: that number has to be smaller than the page has tabbable elements, and the
    // moment a section gains a link it lands on the wrap-around and the test fails for a
    // reason that has nothing to do with smooth scrolling.
    let lastFocused = "";
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press("Tab");
      const state = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el || el === document.body) {
          return { tag: "BODY", scrolled: false };
        }
        return { tag: el.tagName, scrolled: window.scrollY > window.innerHeight / 2 };
      });
      lastFocused = state.tag;
      if (state.scrolled) {
        break;
      }
    }
    expect(["A", "BUTTON", "INPUT"]).toContain(lastFocused);
    expect(await page.evaluate(() => window.scrollY)).toBeGreaterThan(0);

    // Give Lenis its animation window, then check the focused element is really on screen.
    await page.waitForTimeout(1500);
    const visible = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) {
        return null;
      }
      const rect = el.getBoundingClientRect();
      return rect.top >= 0 && rect.bottom <= window.innerHeight;
    });
    expect(visible).toBe(true);
  });
});
