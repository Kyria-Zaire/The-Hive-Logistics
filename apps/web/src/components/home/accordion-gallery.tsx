"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { KeyboardEvent, MouseEvent } from "react";
import Image from "next/image";
import Link from "next/link";
import { gsap } from "gsap";

export type AccordionItem = {
  image: string;
  label: string;
  description?: string;
  link?: string;
  alt?: string;
};

type AccordionGalleryProps = {
  items: AccordionItem[];
  defaultIndex?: number;
  accentColor?: string;
  overlayColor?: string;
  textColor?: string;
  height?: number;
  gap?: number;
  radius?: number;
  expandRatio?: number;
  orientation?: "horizontal" | "vertical";
  duration?: number;
  ease?: string;
  parallax?: number;
  tilt?: number;
  stagger?: number;
  trigger?: "hover" | "click";
  showLabels?: boolean;
  grayscale?: boolean;
  className?: string;
  /** Announced on the list. Required: a list of links with no name is a dead end for AT. */
  label: string;
};

/**
 * TICKET 25 — the services as an accordion: one panel open, the others folded back.
 *
 * Adapted from the reference implementation in four places, each for a reason worth keeping:
 * `next/image` rather than a raw `<img>` (the three sources weigh 9.1 Mo between them), a
 * `ul`/`li`/`a` skeleton rather than `role="listitem"` on the anchors (which would have taken
 * the link role away from assistive technology), a ResizeObserver guard so the unit tests can
 * render the page at all, and a named export like the rest of the codebase.
 */
export function AccordionGallery({
  items,
  defaultIndex = 0,
  accentColor = "#DC2626",
  overlayColor = "#0A0A0A",
  textColor = "#FFFFFF",
  height = 460,
  gap = 10,
  radius = 16,
  expandRatio = 0.52,
  orientation = "horizontal",
  duration = 0.6,
  ease = "power3.out",
  parallax = 0.5,
  tilt = 8,
  stagger = 0.06,
  trigger = "hover",
  showLabels = true,
  grayscale = true,
  className = "",
  label,
}: AccordionGalleryProps) {
  const rootRef = useRef<HTMLUListElement>(null);
  const panelRefs = useRef<(HTMLLIElement | null)[]>([]);
  const linkRefs = useRef<(HTMLElement | null)[]>([]);
  const mediaRefs = useRef<(HTMLSpanElement | null)[]>([]);
  const barRefs = useRef<(HTMLSpanElement | null)[]>([]);
  const textRefs = useRef<(HTMLSpanElement | null)[]>([]);
  const descRefs = useRef<(HTMLSpanElement | null)[]>([]);
  const tlRef = useRef<gsap.core.Timeline | null>(null);
  const firstRunRef = useRef(true);
  const mediaSizeRef = useRef(320);

  const vertical = orientation === "vertical";
  const count = items.length;
  const [active, setActive] = useState(Math.min(Math.max(defaultIndex, 0), count - 1));

  const prefersReduced =
    typeof window !== "undefined" && typeof window.matchMedia === "function"
      ? window.matchMedia("(prefers-reduced-motion: reduce)").matches
      : false;

  const applyLayout = useCallback(
    (animate: boolean) => {
      const panels = panelRefs.current;
      if (panels.length === 0) {
        return;
      }

      const ratio = Math.min(Math.max(expandRatio, 0.2), 0.9);
      const grow = count > 1 ? (ratio * (count - 1)) / (1 - ratio) : 1;
      const mediaSize = mediaSizeRef.current;

      tlRef.current?.kill();
      const dur = animate && !prefersReduced ? duration : 0;
      const tl = gsap.timeline();

      panels.forEach((panel, i) => {
        if (!panel) {
          return;
        }
        const isActive = i === active;
        const media = mediaRefs.current[i];
        const bar = barRefs.current[i];
        const text = textRefs.current[i];
        const desc = descRefs.current[i];

        const rot = isActive ? 0 : i < active ? tilt : -tilt;
        const rotProp = vertical ? { rotateX: -rot } : { rotateY: rot };

        tl.to(panel, { flexGrow: isActive ? grow : 1, ...rotProp, duration: dur, ease }, 0);

        if (media) {
          const drift = Math.max(-1.5, Math.min(1.5, active - i));
          const shift = drift * parallax * mediaSize * 0.06;
          tl.to(
            media,
            {
              xPercent: -50,
              yPercent: -50,
              x: vertical ? 0 : isActive ? 0 : shift,
              y: vertical ? (isActive ? 0 : shift) : 0,
              "--ag-gray": grayscale && !isActive ? 1 : 0,
              "--ag-dim": isActive ? 0 : 0.35,
              duration: dur,
              ease,
            },
            0,
          );
        }

        if (showLabels && bar && text) {
          if (isActive) {
            tl.to(
              [bar, text],
              { opacity: 1, x: 0, duration: dur, ease, stagger: prefersReduced ? 0 : stagger },
              0,
            );
            if (desc) {
              tl.to(desc, { opacity: 1, y: 0, duration: dur, ease }, 0.1);
            }
          } else {
            tl.to([bar, text], { opacity: 0, x: -14, duration: dur * 0.6, ease }, 0);
            if (desc) {
              tl.to(desc, { opacity: 0, y: 8, duration: dur * 0.5, ease }, 0);
            }
          }
        }
      });

      tlRef.current = tl;
    },
    [
      active,
      count,
      expandRatio,
      duration,
      ease,
      vertical,
      tilt,
      parallax,
      grayscale,
      showLabels,
      stagger,
      prefersReduced,
    ],
  );

  useEffect(() => {
    const el = rootRef.current;
    if (!el) {
      return;
    }

    const measure = () => {
      const rect = el.getBoundingClientRect();
      const total = vertical ? rect.height : rect.width;
      const usable = Math.max(total - gap * (count - 1), 120);
      const size = Math.max(140, usable * Math.min(Math.max(expandRatio, 0.2), 0.9) * 1.22);
      mediaSizeRef.current = size;
      el.style.setProperty("--ag-media-size", `${size}px`);
      applyLayout(!firstRunRef.current);
    };

    measure();

    // jsdom has no ResizeObserver, and the unit tests render this page.
    if (typeof ResizeObserver === "undefined") {
      return;
    }
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, [applyLayout, gap, count, expandRatio, vertical]);

  useEffect(() => {
    applyLayout(!firstRunRef.current);
    firstRunRef.current = false;
  }, [applyLayout]);

  useEffect(
    () => () => {
      tlRef.current?.kill();
    },
    [],
  );

  // Read from the event, not from a media query: a tap fires a synthetic mouseenter before its
  // click, which opened the panel so the click then saw it as already active and let the
  // navigation through — the first tap left the page instead of showing what it was for.
  // `pointerType` says what actually happened; `(hover: hover)` only says what the device
  // claims it can do, and emulated touch still answers yes.
  const handleEnter = (index: number, pointerType: string) => {
    if (trigger !== "hover" || pointerType !== "mouse") {
      return;
    }
    setActive(index);
  };

  // Keyboard focus opens the panel; a tap must not. Tapping a link focuses it, which opened
  // the panel before the click ran, so the click saw it as already active and followed the
  // href — the first tap left the page. `:focus-visible` is the browser's own answer to
  // "was this focus deliberate", which is exactly the distinction wanted here.
  const handleFocus = (index: number, element: HTMLElement) => {
    if (element.matches(":focus-visible")) {
      setActive(index);
    }
  };

  // First tap opens the panel, second follows the link: on a touch screen there is no hover to
  // reveal what the panel is about before committing to it.
  const handleClick = (index: number, event: MouseEvent) => {
    if (index !== active) {
      event.preventDefault();
      setActive(index);
    }
  };

  // Focus moves with the selection. Opening a panel without taking the focus along left the
  // arrows computing from whichever panel was still focused: a second ArrowRight did nothing,
  // and ArrowLeft jumped to the far end instead of stepping back.
  const goTo = (index: number) => {
    const next = (index + count) % count;
    setActive(next);
    linkRefs.current[next]?.focus();
  };

  const handleKeyDown = (index: number, event: KeyboardEvent) => {
    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      event.preventDefault();
      goTo(index + 1);
    } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      event.preventDefault();
      goTo(index - 1);
    } else if (event.key === "Home") {
      event.preventDefault();
      goTo(0);
    } else if (event.key === "End") {
      event.preventDefault();
      goTo(count - 1);
    }
  };

  return (
    <ul
      ref={rootRef}
      className={`accordion-gallery${vertical ? " accordion-gallery--vertical" : ""}${
        className ? ` ${className}` : ""
      }`}
      style={{
        "--ag-accent": accentColor,
        "--ag-overlay": overlayColor,
        "--ag-text": textColor,
        "--ag-gap": `${gap}px`,
        "--ag-radius": `${radius}px`,
        "--ag-height": `${vertical ? Math.round(height * 1.6) : height}px`,
      } as React.CSSProperties}
      aria-label={label}
    >
      {items.map((item, index) => {
        const isActive = index === active;
        const content = (
          <>
            <span className="ag-panel__frame">
              <span
                className="ag-panel__media"
                ref={(el) => {
                  mediaRefs.current[index] = el;
                }}
              >
                <Image
                  src={item.image}
                  alt={item.alt ?? ""}
                  aria-hidden={item.alt ? undefined : true}
                  fill
                  sizes="(min-width: 1024px) 55vw, (min-width: 768px) 65vw, 100vw"
                  quality={75}
                  draggable={false}
                />
              </span>
              <span className="ag-panel__overlay" aria-hidden="true" />
            </span>
            {showLabels ? (
              <span className="ag-panel__label">
                <span
                  aria-hidden="true"
                  className="ag-panel__bar"
                  ref={(el) => {
                    barRefs.current[index] = el;
                  }}
                />
                <span className="ag-panel__text-wrap">
                  <span
                    className="ag-panel__text"
                    ref={(el) => {
                      textRefs.current[index] = el;
                    }}
                  >
                    {item.label}
                  </span>
                  {item.description ? (
                    <span
                      className="ag-panel__desc"
                      ref={(el) => {
                        descRefs.current[index] = el;
                      }}
                    >
                      {item.description}
                    </span>
                  ) : null}
                </span>
              </span>
            ) : null}
          </>
        );

        return (
          <li
            key={item.label}
            className={`ag-panel${isActive ? " ag-panel--active" : ""}`}
            style={{ borderRadius: `${radius}px` }}
            ref={(el) => {
              panelRefs.current[index] = el;
            }}
          >
            {item.link ? (
              <Link
                href={item.link}
                className="ag-panel__link"
                ref={(el) => {
                  linkRefs.current[index] = el;
                }}
                onClick={(event) => handleClick(index, event)}
                onPointerEnter={(event) => handleEnter(index, event.pointerType)}
                onFocus={(event) => handleFocus(index, event.currentTarget)}
                onKeyDown={(event) => handleKeyDown(index, event)}
                aria-current={isActive ? "true" : undefined}
              >
                {content}
              </Link>
            ) : (
              <span
                className="ag-panel__link"
                role="button"
                tabIndex={0}
                ref={(el) => {
                  linkRefs.current[index] = el;
                }}
                onClick={(event) => handleClick(index, event)}
                onPointerEnter={(event) => handleEnter(index, event.pointerType)}
                onFocus={(event) => handleFocus(index, event.currentTarget)}
                onKeyDown={(event) => handleKeyDown(index, event)}
                aria-current={isActive ? "true" : undefined}
                aria-label={item.label}
              >
                {content}
              </span>
            )}
          </li>
        );
      })}
    </ul>
  );
}
