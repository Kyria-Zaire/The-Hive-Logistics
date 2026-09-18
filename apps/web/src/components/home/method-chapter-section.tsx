"use client";

import { useEffect, useRef, useState } from "react";
import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";
import { CtaLink } from "@/components/ui/cta-link";

export function MethodChapterSection() {
  const { methodChapter } = homeContent;
  const timelineRef = useRef<HTMLOListElement>(null);
  const [timelineReady, setTimelineReady] = useState(false);
  const [timelineVisible, setTimelineVisible] = useState(false);

  useEffect(() => {
    const timeline = timelineRef.current;
    if (!timeline) {
      return;
    }
    if (typeof IntersectionObserver === "undefined") {
      return;
    }

    const readyFrame = window.requestAnimationFrame(() => {
      setTimelineReady(true);
    });
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry?.isIntersecting) {
          return;
        }
        setTimelineVisible(true);
        observer.disconnect();
      },
      { threshold: 0.2 },
    );
    observer.observe(timeline);

    return () => {
      window.cancelAnimationFrame(readyFrame);
      observer.disconnect();
    };
  }, []);

  return (
    <section
      aria-labelledby="methode-hive"
      className="bg-[var(--bg-primary)] py-[var(--space-6)] lg:py-[var(--space-7)]"
    >
      <div className="thl-container">
        <p className="text-caption text-[var(--text-muted)]">{methodChapter.eyebrow}</p>
        <h2 id="methode-hive" className="text-display-m mt-4 text-[var(--text-primary)]">
          {methodChapter.chapterTitle}
        </h2>

        <div className="mt-[var(--space-6)]">
          <ol
            ref={timelineRef}
            data-ready={timelineReady}
            data-visible={timelineVisible}
            className="thl-process-timeline relative flex flex-col gap-[var(--space-5)] border-l border-[var(--border)] pl-[var(--space-4)] lg:flex-row lg:gap-0 lg:border-l-0 lg:border-t lg:pl-0"
          >
            {methodChapter.steps.map((step) => (
              <li
                key={step.num}
                className="thl-process-step relative lg:flex-1 lg:pr-[var(--space-5)] lg:pt-[var(--space-5)] lg:last:pr-0"
                style={{ "--step-index": Number(step.num) - 1 } as React.CSSProperties}
              >
                {/* 400 is the lightest weight Instrument Sans ships: the scale carries the lightness. */}
                <span className="text-display-l block font-normal text-[var(--accent)]">
                  {step.num}
                </span>
                <h3 className="text-heading mt-[var(--space-4)] text-[var(--text-primary)]">
                  {step.title}
                </h3>
                <p className="text-body mt-[var(--space-3)] text-[var(--text-secondary)]">
                  {step.text}
                </p>
              </li>
            ))}
          </ol>
          <p className="text-body mt-[var(--space-5)] max-w-2xl text-[var(--text-muted)]">
            {methodChapter.note}
          </p>
        </div>

        <div className="mt-[var(--space-6)] border-t border-[var(--border)] pt-[var(--space-6)]">
          <h3 className="text-display-m text-[var(--text-primary)]">
            {methodChapter.principlesTitle}
          </h3>
          <ol className="mt-[var(--space-5)] grid grid-cols-1 gap-[var(--space-5)] md:grid-cols-2 lg:grid-cols-4">
            {methodChapter.principles.map((principle) => (
              <li key={principle.num}>
                <span className="text-caption text-[var(--text-secondary)]">{principle.num}</span>
                <p className="text-heading mt-[var(--space-3)] text-[var(--text-primary)]">
                  {principle.title}
                </p>
                <p className="text-body mt-[var(--space-3)] text-[var(--text-secondary)]">
                  {principle.text}
                </p>
              </li>
            ))}
          </ol>
          <div className="mt-[var(--space-6)]">
            <CtaLink href={ROUTES.quote} variant="outline">
              {methodChapter.cta}
            </CtaLink>
          </div>
        </div>
      </div>
      <style jsx global>{`
        .thl-process-timeline[data-ready="true"] .thl-process-step {
          opacity: 0;
          transform: translateY(20px);
        }

        .thl-process-timeline[data-visible="true"] .thl-process-step {
          animation: thl-process-step-enter 700ms var(--ease-lux) forwards;
          animation-delay: calc(var(--step-index) * 150ms);
        }

        @keyframes thl-process-step-enter {
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .thl-process-timeline[data-ready="true"] .thl-process-step {
            animation: none;
            opacity: 1;
            transform: none;
          }
        }
      `}</style>
    </section>
  );
}
