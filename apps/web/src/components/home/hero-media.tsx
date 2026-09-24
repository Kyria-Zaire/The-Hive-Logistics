"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { getImageProps } from "next/image";

/**
 * The opening frame of each clip, extracted from the files themselves.
 *
 * It used to be a different photograph altogether, and the handover showed: the still painted
 * at 469ms, the video only had a frame at 1027ms, and the crossfade ran until 1742ms — well
 * over a second of watching one picture turn into another on every reload. Serving the video's
 * own first frame makes that second invisible: what paints first is what the video is about to
 * play. It is also what reduced motion gets, which keeps the two paths looking like one design.
 */
const HERO_DESKTOP = {
  src: "/images/hero/hero-poster-desktop.jpg",
  width: 1920,
  height: 1080,
} as const;

const HERO_MOBILE = {
  src: "/images/hero/hero-poster-mobile.jpg",
  width: 720,
  height: 1280,
} as const;

/** 1920x1080, 1.65 Mo. */
const HERO_VIDEO_DESKTOP = "/videos/hero-desktop.mp4";
/** 720x1280, 633 Ko — framed for the crop rather than cropped into it. */
const HERO_VIDEO_MOBILE = "/videos/hero-mobile.mp4";

/**
 * Every viewport, on a CTO call: the loop is the hero on a phone as much as on a desktop.
 * Reduced motion is the one thing that still turns it off — a looping shot is exactly what
 * that preference asks us to leave alone — and the still then is not a fallback but the
 * design.
 */
const VIDEO_WANTED = "(prefers-reduced-motion: no-preference)";

/**
 * Below this, the portrait cut. Phones only: at 768 the portrait file is upscaled past its
 * own 721px width and loses 170px top and bottom, which read as a heavy zoom. Tablets keep
 * the wide cut, where they have the width to carry it.
 */
const SMALL_SCREEN = "(max-width: 767px)";

/**
 * Subscribed to rather than read in an effect: the store hook hydrates against the server
 * answer and then swaps in the client's, so the markup React hydrates is the markup the
 * server sent — no mismatch, and no first frame with the video already in the tree.
 * The visitor can turn reduced motion on, or drag the window across the breakpoint.
 */
const watch = (query: string) => (onChange: () => void) => {
  if (typeof window.matchMedia !== "function") {
    return () => {};
  }
  const list = window.matchMedia(query);
  list.addEventListener("change", onChange);
  return () => list.removeEventListener("change", onChange);
};

const matches = (query: string) => () =>
  typeof window.matchMedia === "function" && window.matchMedia(query).matches;

const watchVideoWanted = watch(VIDEO_WANTED);
const videoWanted = matches(VIDEO_WANTED);
const watchSmallScreen = watch(SMALL_SCREEN);
const smallScreen = matches(SMALL_SCREEN);

/** The server has no viewport and no preference: it always sends the still, wide cut. */
const onServer = () => false;

/**
 * Keyed on its source by the parent, so a viewport crossing the breakpoint replaces the
 * element outright. Swapping the `<source>` of a playing video changes nothing on its own —
 * it takes a `load()` — and a fresh element also resets the fade, which would otherwise show
 * the new file at full opacity before it had a frame to show.
 */
function HeroVideo({ src, framing }: { src: string; framing: string }) {
  const [playing, setPlaying] = useState(false);
  const video = useRef<HTMLVideoElement>(null);

  // A loop decoding behind five screens of scrolled content costs frames on the sections
  // below and battery everywhere, and no browser pauses it for us.
  useEffect(() => {
    const element = video.current;
    if (!element || typeof IntersectionObserver === "undefined") {
      return;
    }

    const observer = new IntersectionObserver(([entry]) => {
      if (entry?.isIntersecting) {
        // Refused autoplay leaves the still in place, which is what it is there for.
        void element.play().catch(() => setPlaying(false));
      } else {
        element.pause();
      }
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  return (
    <video
      ref={video}
      autoPlay
      muted
      loop
      playsInline
      preload="metadata"
      aria-hidden="true"
      // No `poster`: the still underneath already plays that part, optimized and sized for the
      // viewport. Pointing `poster` at the raw file would have fetched 1.3 Mo of JPEG a second
      // time, against the very LCP this is meant to protect.
      onPlaying={() => setPlaying(true)}
      // brightness: both clips are graded lighter than the stills they replace, and their
      // brightest moments took the eyebrow under the 4.5:1 it needs at 14px — 3.95:1 at
      // 1024x768 on the wide cut, 3.72:1 at 360x640 on the portrait one. Sampled every third
      // of a second across both files, 0.85 left only 4.75:1 at the tightest; 0.8 holds
      // 5.25:1 there and 5.9:1 on the wide cut, which is the margin worth having between the
      // frames a sample cannot reach.
      // 200ms, not 700: the frame underneath is this clip's own opening image, so the fade has
      // nothing left to disguise — it only has to cover the decode. Seven hundred of them were
      // the largest single slice of the second-long handover this used to show.
      className={`absolute inset-0 size-full object-cover brightness-[0.8] transition-opacity duration-200 ease-[var(--ease-lux)] ${framing} ${
        playing ? "opacity-100" : "opacity-0"
      }`}
    >
      <source src={src} type="video/mp4" />
    </video>
  );
}

/**
 * TICKET 22 — the hero backdrop: an art-directed still, with a silent loop laid over it.
 *
 * The still is server-rendered and stays: it is the LCP element, it is what shows before the
 * first frame arrives, and it is the whole picture wherever the video is not wanted. The
 * video mounts only once the client has said it wants one, and in the cut that fits the
 * screen asking for it.
 */
export function HeroMedia() {
  const wanted = useSyncExternalStore(watchVideoWanted, videoWanted, onServer);
  const small = useSyncExternalStore(watchSmallScreen, smallScreen, onServer);
  const source = small ? HERO_VIDEO_MOBILE : HERO_VIDEO_DESKTOP;

  // The portrait cut is framed for the shape it is served to and stays centred. The wide one
  // still loses 58% of its width on a tablet, and its centre there is smoke and a brick wall —
  // held to the right, the tail-light signature stays in shot, and it measured better behind
  // the text too (9.20:1 against 7.07:1 at 768). Past lg only 80px a side go, so the frame
  // returns to where the shot was composed.
  const framing = small ? "object-center" : "object-[85%_50%] lg:object-center";

  // priority only disables lazy loading here: fetchPriority is a separate prop in next/image.
  const common = {
    alt: "",
    sizes: "100vw",
    priority: true,
    fetchPriority: "high" as const,
  };
  const {
    props: { srcSet: desktopSrcSet },
  } = getImageProps({ ...common, ...HERO_DESKTOP });
  const {
    props: { srcSet: mobileSrcSet, ...imgProps },
  } = getImageProps({ ...common, ...HERO_MOBILE });

  return (
    <div
      className="absolute inset-0 overflow-hidden bg-[var(--bg-primary)]"
      aria-hidden="true"
    >
      {/* Art direction on the same 768px line the video switches at, so the frame that paints
          is the frame the clip about to load will open on — same cut, same crop, same grading
          as the `brightness` and `object-position` the video carries. */}
      <picture className="block size-full">
        <source media="(min-width: 768px)" srcSet={desktopSrcSet} />
        <source srcSet={mobileSrcSet} />
        <img
          {...imgProps}
          alt=""
          className="size-full object-cover object-center brightness-[0.8] md:object-[85%_50%] lg:object-center"
        />
      </picture>

      {wanted ? <HeroVideo key={source} src={source} framing={framing} /> : null}
    </div>
  );
}
