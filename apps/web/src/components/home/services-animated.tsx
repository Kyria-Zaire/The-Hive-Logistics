"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { easeLux } from "@/lib/ease-lux";

/**
 * TICKET 21 — reveals the services gallery; renders nothing itself.
 *
 * The section is a Server Component: its titles, images and copy are in the HTML before any
 * JavaScript runs, and they are opaque there. This only takes them down and brings them back,
 * which keeps the section readable if the script never arrives — and keeps GSAP in the chunk
 * of the one route that uses it.
 */
export function ServicesAnimated() {
  const anchor = useRef<HTMLSpanElement>(null);

  useGSAP(
    () => {
      const root = anchor.current?.closest("section");
      if (!root) {
        return;
      }

      // Reduced motion: the gallery is already in place in the HTML, so not building the
      // timeline is the whole implementation. The matchMedia call doubles as a capability
      // guard — ScrollTrigger.register uses it, and jsdom has none.
      if (
        typeof window.matchMedia !== "function" ||
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ) {
        return;
      }

      // Registered here rather than at module scope: importing this file must not touch the
      // DOM, otherwise the unit tests fail before a single component renders.
      gsap.registerPlugin(ScrollTrigger, useGSAP);

      // The gallery arrives as one block. It used to be three tiles staggered 150ms apart;
      // the accordion runs its own choreography between the panels, and a second one layered
      // on top of it read as two animations fighting over the same elements.
      const gallery = root.querySelector<HTMLElement>(".accordion-gallery");
      if (!gallery) {
        return;
      }

      gsap.from(gallery, {
        opacity: 0,
        y: 40,
        duration: 0.7,
        ease: easeLux(),
        scrollTrigger: {
          trigger: root,
          // The section's top a third of the way up the viewport: the gallery is tall, and
          // starting any later left it half-faded at the bottom of the screen.
          start: "top 70%",
          // Played once. A block that replayed on every pass turned a long page into a
          // flickering one, and scrolling back up is not a reason to re-announce it.
          once: true,
        },
      });
    },
    // No dependencies: useGSAP would re-run the callback without reverting the previous
    // context, and the second `from()` would capture the first one's start values as targets.
    { dependencies: [] },
  );

  return <span ref={anchor} hidden />;
}
