import fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";

const captureDir =
  process.env.THL_CAPTURE_DIR ??
  path.join(process.env.TEMP ?? process.cwd(), "thl-home-review");

const viewports = [
  { width: 320, height: 568, file: "home-320-viewport.png" },
  { width: 390, height: 844, file: "home-390-viewport.png" },
  { width: 1440, height: 900, file: "home-1440-viewport.png" },
  { width: 1920, height: 1080, file: "home-1920-viewport.png" },
] as const;

test.describe("Hero viewport captures", () => {
  test("génère les PNG viewport exacts", async ({ page }) => {
    fs.mkdirSync(captureDir, { recursive: true });
    await page.emulateMedia({ reducedMotion: "reduce" });

    for (const vp of viewports) {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto("/");
      const target = path.join(captureDir, vp.file);
      await page.screenshot({ path: target, fullPage: false, animations: "disabled" });

      const buffer = fs.readFileSync(target);
      expect(buffer.length).toBeGreaterThan(1000);
      const pngWidth = buffer.readUInt32BE(16);
      const pngHeight = buffer.readUInt32BE(20);
      expect({ width: pngWidth, height: pngHeight }).toEqual({
        width: vp.width,
        height: vp.height,
      });

      const dimensions = await page.evaluate(() => ({
        innerWidth: window.innerWidth,
        innerHeight: window.innerHeight,
      }));
      expect(dimensions.innerWidth).toBe(vp.width);
      expect(dimensions.innerHeight).toBe(vp.height);
    }

    if (fs.existsSync(path.join(captureDir, "home-1920.png"))) {
      fs.unlinkSync(path.join(captureDir, "home-1920.png"));
    }
  });
});
