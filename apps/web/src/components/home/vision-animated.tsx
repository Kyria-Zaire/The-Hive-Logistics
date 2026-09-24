"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { useSmoothScroll } from "@/components/providers/smooth-scroll-provider";
import { easeLux } from "@/lib/ease-lux";

/** Where an unread word sits: dim enough to read as pending, not so dim it looks broken. */
const WORD_DIM = 0.15;
/** Seconds between two words on the timeline, remapped onto the track by the scrub. */
const WORD_STAGGER = 0.05;
/*
 * There is no blur here, and that is a measured decision rather than an omission. Fading a
 * blur radius cost the desktop about nine frames a second on this section — 46-50 i/s with the
 * filter on the 69 words, 51 with a single one over the paragraph, 60 with none. The element
 * count was never the problem: an animated radius makes Chromium re-rasterise the area every
 * frame, and promoting the layer (`will-change`, `contain`, `translateZ`) only made it worse.
 * The reveal carries on opacity alone, which the compositor gives away for free.
 */

/**
 * TICKET 24 — reads the vision statement out word by word; renders nothing itself.
 *
 * The section is a Server Component: the sentence is in the HTML, whole and opaque, before any
 * JavaScript runs. This only dims the words and brings them back as the screen is scrolled.
 */
export function VisionAnimated() {
  const lenis = useSmoothScroll();
  const anchor = useRef<HTMLSpanElement>(null);
  const [layout, setLayout] = useState(0);

  // The blur is decided once, by breakpoint, so a window dragged across 1024px would otherwise
  // keep the wrong decision. Same guard as the other sections: a height-only change under
  // 200px is a mobile browser hiding its address bar mid-scroll, not a resize.
  useEffect(() => {
    let width = window.innerWidth;
    let height = window.innerHeight;
    let pending = 0;

    const settle = () => {
      const resized =
        window.innerWidth !== width || Math.abs(window.innerHeight - height) > 200;
      width = window.innerWidth;
      height = window.innerHeight;
      if (resized) {
        setLayout((n) => n + 1);
      }
    };

    const onResize = () => {
      window.clearTimeout(pending);
      pending = window.setTimeout(settle, 200);
    };

    window.addEventListener("resize", onResize);
    return () => {
      window.clearTimeout(pending);
      window.removeEventListener("resize", onResize);
    };
  }, []);

  useGSAP(
    () => {
      const root = anchor.current?.closest("section");
      if (!root) {
        return;
      }

      // Reduced motion: no timeline at all. The markup's motion-reduce: variants have unpinned
      // the stage, and globals.css holds the words at full opacity — the statement is simply
      // there to read. The matchMedia check doubles as a capability guard: ScrollTrigger
      // .register calls it, and jsdom has no implementation.
      if (
        typeof window.matchMedia !== "function" ||
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ) {
        return;
      }

      // Registered here rather than at module scope: importing this file must not touch the
      // DOM, otherwise the unit tests fail before a single component renders.
      gsap.registerPlugin(ScrollTrigger, useGSAP);

      const track = root.querySelector<HTMLElement>(".thl-vision-track");
      const intro = root.querySelector<HTMLElement>(".thl-vision-intro");
      const words = root.querySelectorAll<HTMLElement>(".thl-vision-body .word");

      // The heading arrives on its own, once, rather than being tied to the scrub: it is the
      // frame around the statement, not part of the reading.
      if (intro) {
        gsap.from(intro, {
          opacity: 0,
          y: 20,
          duration: 0.8,
          ease: easeLux(),
          scrollTrigger: { trigger: root, start: "top 70%", once: true },
        });
      }

      if (!track || words.length === 0) {
        return;
      }

      // The words light up one after the other, across the whole track.
      gsap.fromTo(
        words,
        { opacity: WORD_DIM },
        {
          opacity: 1,
          stagger: WORD_STAGGER,
          ease: "none",
          scrollTrigger: {
            trigger: track,
            start: "top top",
            end: "bottom bottom",
            scrub: 1,
          },
        },
      );
    },
    // revertOnUpdate is what makes the rebuild safe: without it useGSAP re-runs the callback
    // and leaves the previous context standing, so a second `fromTo` would capture the first
    // one's frozen start values as its targets.
    { dependencies: [layout], revertOnUpdate: true },
  );

  // The provider owns Lenis' rAF loop; ScrollTrigger only needs to be told when it moves.
  // Kept out of useGSAP so the timeline is never rebuilt when the instance appears.
  useEffect(() => {
    if (!lenis) {
      return;
    }
    lenis.on("scroll", ScrollTrigger.update);
    return () => {
      lenis.off("scroll", ScrollTrigger.update);
    };
  }, [lenis]);

  return <span ref={anchor} hidden />;
}
