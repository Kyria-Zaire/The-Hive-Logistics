"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { useSmoothScroll } from "@/components/providers/smooth-scroll-provider";
import { TRACK_TRAVEL } from "@/components/home/method-road";

/**
 * TICKET 20 — animates the method section's existing DOM; renders nothing itself.
 *
 * The section is a Server Component: its texts, the cars and the roads are in the HTML
 * before any JavaScript runs. This client component only amplifies them, which also
 * keeps GSAP in the chunk of the single route that uses it.
 *
 * One timeline for every screen size: the staging differs in CSS, but every distance here
 * is measured from the live layout, so the same code drives phone, tablet and desktop.
 */
export function MethodAnimated() {
  const lenis = useSmoothScroll();
  const anchor = useRef<HTMLSpanElement>(null);
  const [layout, setLayout] = useState(0);

  // Every distance below is read from the live layout when the timelines are built, and a
  // window resized after load leaves the lot stale: maximised from 1440 to 1900, the car
  // entered the principles scene with 222px of itself already on screen and left it with as
  // much still showing. Rebuilding on a real size change recomputes everything from the
  // layout it now has — simpler than making each distance dynamic, and it covers the reveal
  // cues too, which are positions in a timeline and cannot be function-based.
  useEffect(() => {
    let width = window.innerWidth;
    let height = window.innerHeight;
    let pending = 0;

    const settle = () => {
      // Height alone and by little is a mobile browser hiding its address bar mid-scroll,
      // not a resize; rebuilding there would rebuild under the visitor's thumb.
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

      // Reduced motion: the static DOM already reads correctly (roads drawn, steps opaque),
      // so we simply never build the timeline. The sticky layout is CSS and stays.
      // The matchMedia check doubles as a capability guard: ScrollTrigger.register calls it,
      // and jsdom has no implementation.
      if (
        typeof window.matchMedia !== "function" ||
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ) {
        return;
      }

      // Registered here rather than at module scope: importing this file must not touch
      // the DOM, otherwise the unit tests fail before a single component renders.
      gsap.registerPlugin(ScrollTrigger, useGSAP);

      const tracks = root.querySelectorAll<HTMLElement>(".thl-method-road-track");
      const car = root.querySelector<HTMLElement>(".thl-method-car");
      const steps = root.querySelectorAll<HTMLElement>(".thl-method-step");
      const list = root.querySelector<HTMLElement>(".thl-method-list");
      const approach = root.querySelector<HTMLElement>(".thl-method-approach");
      const carriage = root.querySelector<HTMLElement>(".thl-method-carriage");
      const line = root.querySelector<HTMLElement>(".thl-method-line");
      const window_steps = root.querySelector<HTMLElement>(".thl-method-steps");

      const principlesTrack = root.querySelector<HTMLElement>(".thl-principles-scroll");
      const principlesStage = principlesTrack?.firstElementChild as HTMLElement | null;
      const principlesCar = root.querySelector<HTMLElement>(".thl-principles-car");
      const principlesBody = root.querySelector<HTMLElement>(".thl-principles-car-body");
      const principles = [...root.querySelectorAll<HTMLElement>(".thl-principle")];

      // The road is the track's parent; it goes out with the car so nothing is left hanging
      // above the line once the car has gone under.
      const roads = [...tracks]
        .map((t) => t.parentElement)
        .filter((el): el is HTMLElement => el !== null);

      // The trigger is the scroll track, not the whole section: the animation must finish
      // exactly when the pin releases, before the principles block scrolls in.
      const scrollTrack = root.querySelector<HTMLElement>(".thl-method-scroll") ?? root;
      const pinned = scrollTrack.firstElementChild as HTMLElement | null;

      // --------------------------------------------------------------------------------
      // The car rides a sticky screen, so once that screen is stuck its rect sits a whole
      // screen below where the car actually rests — and a rebuild triggered while the visitor
      // was halfway down the page measured it there, then sent the car driving back up the
      // road. offsetTop is no help: for a sticky element Chrome reports the stuck offset, not
      // the static one. So the screen is pinned back to its static place for the length of the
      // reading, which is the only measurement that does not depend on where the page happens
      // to be. `relative`, not `static`: the car inside is positioned against this screen, and
      // taking it out of the positioned flow sent that 46% off the 320vh track instead.
      //
      // Everything is read here, before a single tween exists: a `fromTo` applies its start
      // value the moment it is created, so measuring afterwards read the car already lifted a
      // screen above its resting place, and the dive was handed that much extra travel —
      // hurling the car through the separator line instead of letting it sink into it.
      // --------------------------------------------------------------------------------
      const carLayer = root.querySelector<HTMLElement>(".thl-method-car-layer");
      const previousPosition = carLayer?.style.position ?? "";
      if (carLayer) {
        carLayer.style.position = "relative";
      }

      // How far above its resting place the car has to start so it comes out from under the
      // boundary with the section above rather than fading in mid-air.
      const entry = approach
        ? approach.getBoundingClientRect().bottom - root.getBoundingClientRect().top
        : 0;

      // Once the pin releases, the screen sits this much lower than where it is measured now.
      const released = pinned ? scrollTrack.offsetHeight - pinned.offsetHeight : 0;

      // Travel that puts the car's roof exactly on the separator line: from there down the
      // opaque block owns every pixel, so the car is gone for good.
      const run =
        carriage && line
          ? line.getBoundingClientRect().top - carriage.getBoundingClientRect().top - released
          : 0;

      if (carLayer) {
        carLayer.style.position = previousPosition;
      }

      // Column travel measured from the column itself, so the first step starts centred on
      // the window and the last one ends centred, instead of the column running off the top.
      const listTravel = list ? (list.offsetHeight - (steps[0]?.offsetHeight ?? 0)) / 2 : 0;

      // Main act, while the screen is pinned.
      const timeline = gsap.timeline({
        scrollTrigger: {
          trigger: scrollTrack,
          start: "top top",
          end: "bottom bottom",
          scrub: 1,
        },
      });

      // The car holds its place; the marking streams past it, which is what reads as driving.
      timeline.to(tracks, { y: -TRACK_TRAVEL, ease: "none", duration: 1 }, 0);

      // It breathes on its suspension while the road runs under it.
      if (car) {
        timeline.to(car, { y: 24, scale: 1.04, ease: "none", duration: 1 }, 0);
      }

      // The whole column travels through its window, so each step rises past the car. The
      // window's gradients dissolve them at both edges, which keeps every step fully opaque —
      // and legible — for the whole time it is actually readable.
      if (list) {
        timeline.fromTo(
          list,
          { y: listTravel },
          { y: -listTravel, ease: "none", duration: 1 },
          0,
        );
      }

      // First act: the car comes out from under the boundary with the section above and
      // drives down into place. The section clips itself, so it stays hidden until then.
      if (approach) {
        gsap
          .timeline({
            scrollTrigger: { trigger: root, start: "top bottom", end: "top top", scrub: 1 },
          })
          .fromTo(approach, { y: -entry }, { y: 0, ease: "none", duration: 1 }, 0);
      }

      // Second act: once the screen is released, the car keeps driving down until its roof
      // reaches the line that separates the two halves of the section, and the opaque block
      // below swallows it. The road goes out with it.
      if (carriage && line) {
        gsap
          .timeline({
            scrollTrigger: { trigger: line, start: "top bottom", end: "top center", scrub: 1 },
          })
          .fromTo(carriage, { y: 0 }, { y: run, ease: "none", duration: 1 }, 0)
          // Road and steps clear the stage with it. They sit above the note in the stacking
          // order, and a white marking or a step title landing on that 16px text measured
          // 1.30:1. Only the car keeps going, which is the one crossing we want.
          .to(
            [...roads, window_steps].filter(Boolean),
            { opacity: 0, ease: "power1.in", duration: 1 },
            0,
          );
      }

      // Second scene: the principles. Same staging turned on its side — here the road holds
      // still and the car does the travelling, from one edge of the screen to the other,
      // lighting each principle as it draws level with it.
      if (principlesTrack && principlesStage && principlesCar && principlesBody) {
        const stage = principlesStage.getBoundingClientRect();
        // The photograph is turned a quarter turn, so the box the layout reserves (tall and
        // narrow) and the shape we actually see (wide and short) differ by some 65px on each
        // side. getBoundingClientRect reads the painted box, transform included; offsetWidth
        // would have left that much car hanging at both edges of the screen.
        const body = principlesBody.getBoundingClientRect();

        // A few pixels past each edge, so no anti-aliased sliver survives the crossing.
        const MARGIN = 8;
        const enterFrom = stage.left - body.right - MARGIN;
        const exitTo = stage.right - body.left + MARGIN;

        // The crossing is over before the track lets the screen go: with `scrub` the car
        // trails the scroll by about a second, and the last of that must not spill into the
        // section below.
        const CROSSING = 0.86;

        const crossing = gsap.timeline({
          scrollTrigger: {
            trigger: principlesTrack,
            start: "top top",
            end: "bottom bottom",
            scrub: 1,
          },
        });

        crossing.fromTo(
          principlesCar,
          { x: enterFrom },
          { x: exitTo, ease: "none", duration: CROSSING },
          0,
        );

        // Each principle lights up as the car draws level with it, so they come in one at a
        // time rather than as a block. They come in rather than dim out: text held at a low
        // opacity would sit under the 4.5:1 it needs, as the method steps did at 1.66:1.
        const bodyCentre = (body.left + body.right) / 2;
        const span = exitTo - enterFrom;
        const LEAD = 0.1; // up just before the bonnet reaches it, not once it has gone past
        const GAP = 0.08; // two principles in one column still arrive one after the other

        let previous = -Infinity;
        principles.forEach((principle) => {
          const rect = principle.getBoundingClientRect();
          const level = ((rect.left + rect.right) / 2 - bodyCentre - enterFrom) / span;
          const at = Math.max(
            0,
            Math.min(CROSSING, level * CROSSING - LEAD),
            previous + GAP,
          );
          previous = at;
          crossing.from(principle, { opacity: 0, y: 28, duration: 0.14 }, at);
        });
      }
    },
    // revertOnUpdate is what makes the rebuild safe: without it useGSAP re-runs the callback
    // and leaves the previous context standing, so a second set of timelines would capture
    // the first one's frozen start values as their targets.
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
