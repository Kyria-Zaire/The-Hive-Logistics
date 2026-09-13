import { expect, test } from "@playwright/test";

async function assertPrimaryHeroInFold(
  page: import("@playwright/test").Page,
  viewportHeight: number,
) {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");

  const primary = page.locator('[data-thl-cta="primary-red"]').first();
  await expect(primary).toBeVisible();
  await expect(page.locator('[data-thl-cta="outline"]').first()).toBeAttached();

  const metrics = await page.evaluate(() => {
    const primaryEl = document.querySelector('[data-thl-cta="primary-red"]');
    const h1 = document.getElementById("hero-heading");
    const eyebrow = document.querySelector(".thl-hero-eyebrow");
    const lede = document.querySelector(".thl-hero-lede");
    if (!primaryEl || !h1 || !eyebrow || !lede) {
      return null;
    }
    const pr = primaryEl.getBoundingClientRect();
    const h1r = h1.getBoundingClientRect();
    const er = eyebrow.getBoundingClientRect();
    const lr = lede.getBoundingClientRect();
    const header = document.querySelector("header");
    const hr = header?.getBoundingClientRect();

    return {
      innerHeight: window.innerHeight,
      primaryBottom: pr.bottom,
      primaryTop: pr.top,
      h1Top: h1r.top,
      h1Bottom: h1r.bottom,
      h1LinesVisible: Array.from(h1.getClientRects()).every(
        (rect) => rect.top >= 0 && rect.bottom <= window.innerHeight,
      ),
      eyebrowTop: er.top,
      ledeBottom: lr.bottom,
      headerBottom: hr?.bottom ?? 0,
      horizontalOverflow:
        document.documentElement.scrollWidth > document.documentElement.clientWidth,
    };
  });

  expect(metrics).not.toBeNull();
  if (!metrics) {
    return;
  }

  expect(metrics.innerHeight).toBe(viewportHeight);
  expect(metrics.horizontalOverflow).toBe(false);
  expect(metrics.primaryBottom).toBeLessThanOrEqual(metrics.innerHeight);
  expect(metrics.h1Top).toBeGreaterThanOrEqual(0);
  expect(metrics.h1Bottom).toBeLessThanOrEqual(metrics.innerHeight);
  expect(metrics.h1LinesVisible).toBe(true);
  expect(metrics.eyebrowTop).toBeGreaterThanOrEqual(0);
  expect(metrics.ledeBottom).toBeLessThanOrEqual(metrics.innerHeight);
  expect(metrics.primaryTop).toBeGreaterThanOrEqual(metrics.headerBottom - 2);
}

test.describe("Hero fold", () => {
  test("320×568 — CTA primaire et H1 entièrement visibles", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await assertPrimaryHeroInFold(page, 568);
  });

  test("390×844 — CTA primaire et H1 entièrement visibles", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await assertPrimaryHeroInFold(page, 844);
  });
});
