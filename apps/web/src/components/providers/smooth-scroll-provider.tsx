"use client";

import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import Lenis from "lenis";

/**
 * Smooth scroll (TICKET 19, allégé au TICKET 20).
 *
 * Lenis replaces the browser's wheel physics, so it stays off whenever the visitor
 * asked for reduced motion — the native scroll is then untouched. Touch devices keep
 * their native scrolling too: `syncTouch` is left at its default (false).
 *
 * This provider deliberately knows nothing about GSAP: importing it here would ship
 * ~150 Ko of animation code to every route, including /contact and the legal pages.
 * The section that animates wires ScrollTrigger to this instance through useSmoothScroll().
 */
const SmoothScrollContext = createContext<Lenis | null>(null);

/** The live Lenis instance, or null when smooth scroll is off (reduced motion, SSR, before mount). */
export function useSmoothScroll(): Lenis | null {
  return useContext(SmoothScrollContext);
}

const easeOutExpo = (t: number) => (t === 1 ? 1 : 1 - 2 ** (-10 * t));

export function SmoothScrollProvider({ children }: { children: ReactNode }) {
  const [lenis, setLenis] = useState<Lenis | null>(null);

  useEffect(() => {
    if (typeof window.matchMedia !== "function") {
      return;
    }

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    let instance: Lenis | null = null;
    let frame = 0;

    // Native rAF loop: `raf` takes a millisecond timestamp, which is exactly what rAF hands us.
    const loop = (time: number) => {
      instance?.raf(time);
      frame = window.requestAnimationFrame(loop);
    };

    const start = () => {
      if (instance) {
        return;
      }
      instance = new Lenis({
        duration: 1.2,
        easing: easeOutExpo,
        smoothWheel: true,
        // Lenis owns anchor navigation, otherwise a native jump desyncs its internal target.
        anchors: true,
      });
      frame = window.requestAnimationFrame(loop);
      setLenis(instance);
    };

    const stop = () => {
      if (!instance) {
        return;
      }
      window.cancelAnimationFrame(frame);
      frame = 0;
      instance.destroy();
      instance = null;
      setLenis(null);
    };

    if (!reduced.matches) {
      start();
    }

    // The preference can change while the page is open.
    const onPreferenceChange = () => {
      if (reduced.matches) {
        stop();
      } else {
        start();
      }
    };
    reduced.addEventListener("change", onPreferenceChange);

    return () => {
      reduced.removeEventListener("change", onPreferenceChange);
      stop();
    };
  }, []);

  return <SmoothScrollContext.Provider value={lenis}>{children}</SmoothScrollContext.Provider>;
}
