"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { useSmoothScroll } from "@/components/providers/smooth-scroll-provider";

/** How far past its natural scale the photograph starts, so it settles as the frame opens. */
const MEDIA_ZOOM = 1.35;

/**
 * TICKET 23-BIS — drives the engagements opening; renders nothing itself.
 *
 * One scrubbed timeline for the whole section: the frame opens, the photograph settles out of
 * its zoom, the heading hands over, the three commitments arrive. The section is a Server
 * Component whose content is in the HTML, opaque, before any JavaScript runs — nothing here
 * is load-bearing for reading it.
 */
export function EngagementsAnimated() {
  const lenis = useSmoothScroll();
  const anchor = useRef<HTMLSpanElement>(null);
  const [layout, setLayout] = useState(0);

  // The opening is measured in percentages, but its start values come from the stylesheet and
  // differ per breakpoint. A window dragged across one of them leaves the timeline holding the
  // previous breakpoint's numbers, so it is rebuilt on a real size change — same guard as the
  // method section: a height-only change under 200px is a mobile browser hiding its address
  // bar mid-scroll, not a resize.
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

      // Reduced motion: no timeline at all. The markup's motion-reduce: variants have already
      // unpinned the stage and laid the section out as a stack, and globals.css has dropped
      // the clip-path, so the photograph is simply a block with the text around it.
      if (
        typeof window.matchMedia !== "function" ||
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ) {
        return;
      }

      // Registered here rather than at module scope: importing this file must not touch the
      // DOM, otherwise the unit tests fail before a single component renders.
      gsap.registerPlugin(ScrollTrigger, useGSAP);

      const track = root.querySelector<HTMLElement>(".thl-engagements-track");
      const frame = root.querySelector<HTMLElement>(".thl-engagements-frame");
      const media = root.querySelector<HTMLElement>(".thl-engagements-media");
      const title = root.querySelector<HTMLElement>(".thl-engagements-title");
      const items = root.querySelectorAll<HTMLElement>(".thl-engagement");

      if (!track || !frame) {
        return;
      }

      const timeline = gsap.timeline({
        scrollTrigger: { trigger: track, start: "top top", end: "bottom bottom", scrub: 1 },
      });

      // The frame opens. `to` rather than `fromTo`: the start values are the ones the
      // stylesheet holds for the current breakpoint, so the three openings live in one place
      // and a rebuild after a resize picks up the new one without being told.
      timeline.to(
        frame,
        {
          "--frame-inset-x": "0%",
          "--frame-inset-y": "0%",
          "--frame-radius": "0px",
          ease: "none",
          duration: 1,
        },
        0,
      );

      // The photograph settles out of its zoom over the same beat, so the opening reads as one
      // move rather than a frame growing over a still image.
      if (media) {
        timeline.fromTo(
          media,
          { scale: MEDIA_ZOOM },
          { scale: 1, ease: "none", duration: 1 },
          0,
        );
      }

      // The heading leaves once the frame is well open, and before the commitments land on the
      // same middle of the screen — they never share it.
      if (title) {
        timeline.to(
          title,
          { opacity: 0, y: -28, scale: 1.06, ease: "power2.out", duration: 0.4 },
          0.4,
        );
      }

      // They come in rather than dim out: text held at a low opacity would sit under the
      // 4.5:1 it needs over a photograph.
      if (items.length > 0) {
        timeline.fromTo(
          items,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, stagger: 0.15, duration: 0.3, ease: "power2.out" },
          0.65,
        );
      }
    },
    // revertOnUpdate is what makes the rebuild safe: without it useGSAP re-runs the callback
    // and leaves the previous context standing, so a second timeline would capture the first
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
