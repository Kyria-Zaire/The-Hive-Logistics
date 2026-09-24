/**
 * The `--ease-lux` token, as an ease GSAP can run.
 *
 * GSAP eases are functions of progress; a CSS timing function is not something it reads. Rather
 * than hardcode a second curve here — one that would quietly drift from the token the CSS
 * transitions use — this reads the token itself and evaluates it, so changing `--ease-lux` in
 * globals.css moves the scripted animations with it.
 */

type Ease = string | ((progress: number) => number);

/** Closest built-in, used when the token is missing or is not a cubic-bezier. */
const FALLBACK: Ease = "power4.out";

/** One axis of a cubic Bézier with the endpoints pinned at (0,0) and (1,1). */
const axis = (t: number, p1: number, p2: number) =>
  ((1 - 3 * p2 + 3 * p1) * t + (3 * p2 - 6 * p1)) * t * t + 3 * p1 * t;

/**
 * t for a given x. A closed form exists but is long and ill-conditioned near the ends;
 * 24 bisections land within 1e-7, well under a pixel on any distance we animate.
 */
const solve = (x: number, p1: number, p2: number) => {
  let low = 0;
  let high = 1;
  let t = x;
  for (let i = 0; i < 24; i++) {
    if (axis(t, p1, p2) < x) {
      low = t;
    } else {
      high = t;
    }
    t = (low + high) / 2;
  }
  return t;
};

/** Call from the browser only: it reads the computed value off the document. */
export function easeLux(): Ease {
  if (typeof window === "undefined" || typeof getComputedStyle !== "function") {
    return FALLBACK;
  }

  const token = getComputedStyle(document.documentElement).getPropertyValue("--ease-lux").trim();
  if (!token.startsWith("cubic-bezier")) {
    return FALLBACK;
  }

  const [x1, y1, x2, y2] = (token.match(/-?\d*\.?\d+/g) ?? []).map(Number);
  if (x1 === undefined || y1 === undefined || x2 === undefined || y2 === undefined) {
    return FALLBACK;
  }

  // GSAP requires the ends to be exact; bisection is only near-exact there.
  return (progress: number) =>
    progress <= 0 ? 0 : progress >= 1 ? 1 : axis(solve(progress, x1, x2), y1, y2);
}
