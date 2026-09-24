"use client";

import { useEffect, useRef, useState } from "react";
import { homeContent } from "@/lib/content/home";
import { formatFr } from "@/lib/format-fr";
import { KeyFiguresAnimated } from "@/components/home/key-figures-animated";

export function KeyFiguresSection() {
  const { keyFigures } = homeContent;
  const listRef = useRef<HTMLDListElement>(null);
  const [ready, setReady] = useState(false);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const list = listRef.current;
    if (!list) {
      return;
    }
    if (typeof IntersectionObserver === "undefined") {
      return;
    }

    const readyFrame = window.requestAnimationFrame(() => {
      setReady(true);
    });
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry?.isIntersecting) {
          return;
        }
        setVisible(true);
        observer.disconnect();
      },
      { threshold: 0.2 },
    );
    observer.observe(list);

    return () => {
      window.cancelAnimationFrame(readyFrame);
      observer.disconnect();
    };
  }, []);

  return (
    <section
      aria-label={keyFigures.label}
      className="section-dark py-[var(--space-6)] lg:py-[var(--space-7)]"
    >
      <div className="thl-container">
        <dl
          ref={listRef}
          data-ready={ready}
          data-visible={visible}
          className="thl-figures grid grid-cols-1 gap-[var(--space-5)] lg:grid-cols-3 lg:gap-0"
        >
          {keyFigures.items.map((item, index) => (
            <div
              key={item.label}
              // flex-col-reverse: <dt> stays first in the DOM, the figure reads first on screen.
              className="thl-figure flex flex-col-reverse items-center text-center lg:border-l lg:border-[var(--border)] lg:px-[var(--space-5)] lg:first:border-l-0"
              style={{ "--figure-index": index } as React.CSSProperties}
            >
              <dt className="text-caption mt-[var(--space-3)] text-[var(--text-secondary)]">
                {item.label}
              </dt>
              {/* The final figure is what the HTML carries: without JavaScript the page still
                  says 300, not 0. The count-up resets it before the first paint and counts
                  back up to it. The suffix is a span of its own and is never animated. */}
              <dd className="thl-figure-number text-display-l text-[var(--text-primary)]">
                <span className="thl-figure-value" data-target={item.value}>
                  {formatFr(item.value)}
                </span>
                <span className="thl-figure-suffix">{item.suffix}</span>
              </dd>
            </div>
          ))}
        </dl>
      </div>
      <KeyFiguresAnimated />
      <style jsx global>{`
        .thl-figures[data-ready="true"] .thl-figure {
          opacity: 0;
          transform: translateY(20px);
        }

        .thl-figures[data-visible="true"] .thl-figure {
          animation: thl-figure-enter 700ms var(--ease-lux) forwards;
          animation-delay: calc(var(--figure-index) * 150ms);
        }

        @keyframes thl-figure-enter {
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .thl-figures[data-ready="true"] .thl-figure {
            animation: none;
            opacity: 1;
            transform: none;
          }
        }
      `}</style>
    </section>
  );
}
