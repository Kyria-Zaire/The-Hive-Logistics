"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { formatFr } from "@/lib/format-fr";

/** Long enough to read as counting, short enough that the eye is not kept waiting. */
const COUNT_DURATION = 1.5;
/** Matches the 150ms the CSS stagger already puts between the three blocks. */
const COUNT_STAGGER = 0.15;

/**
 * TICKET 27 — counts the three key figures up from zero; renders nothing itself.
 *
 * The section writes the final numbers into the HTML, so a page without JavaScript states the
 * figures rather than three zeros. This resets them to zero before the first paint — useGSAP
 * runs in a layout effect, so nothing is ever shown counting down — and runs them back up when
 * the block is reached.
 *
 * It only ever writes textContent. The entrance itself stays where it was, in the section's own
 * CSS keyframes: two libraries animating the same opacity would fight over it.
 */
export function KeyFiguresAnimated() {
  const anchor = useRef<HTMLSpanElement>(null);

  useGSAP(
    () => {
      const root = anchor.current?.closest("section");
      if (!root) {
        return;
      }

      const values = root.querySelectorAll<HTMLElement>(".thl-figure-value");
      if (values.length === 0) {
        return;
      }

      // Reduced motion: the numbers are already final in the HTML, so the whole implementation
      // is not to touch them. The matchMedia call doubles as a capability guard —
      // ScrollTrigger.register uses it, and jsdom has none.
      if (
        typeof window.matchMedia !== "function" ||
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ) {
        return;
      }

      // Registered here rather than at module scope: importing this file must not touch the
      // DOM, otherwise the unit tests fail before a single component renders.
      gsap.registerPlugin(ScrollTrigger, useGSAP);

      // Synchronous, inside the layout effect: the browser paints zeros, never the final
      // figure followed by a jump back to zero.
      values.forEach((el) => {
        el.textContent = formatFr(0);
      });

      // Triggered on the list, not the section: the CSS entrance watches the same element with
      // an IntersectionObserver, so the numbers start moving as the blocks come in rather than
      // a section's padding earlier.
      const list = root.querySelector<HTMLElement>(".thl-figures") ?? root;

      values.forEach((el, index) => {
        const target = Number(el.dataset.target);
        if (!Number.isFinite(target)) {
          return;
        }

        const counter = { current: 0 };
        gsap.to(counter, {
          current: target,
          duration: COUNT_DURATION,
          ease: "power2.out",
          delay: index * COUNT_STAGGER,
          onUpdate: () => {
            el.textContent = formatFr(counter.current);
          },
          scrollTrigger: { trigger: list, start: "top 80%", once: true },
        });
      });
    },
    // No dependencies: useGSAP would re-run the callback without reverting the previous
    // context, and a second pass would reset figures that had already counted up.
    { dependencies: [] },
  );

  return <span ref={anchor} hidden />;
}
