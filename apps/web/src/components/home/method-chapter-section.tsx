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
      className="bg-[var(--bg-primary)] py-[var(--space-6)]"
    >
      <div className="thl-container">
        <p className="text-caption text-[var(--text-muted)]">{methodChapter.eyebrow}</p>
        <h2 id="methode-hive" className="text-display-m mt-4 text-[var(--text-primary)]">
          {methodChapter.chapterTitle}
        </h2>

        <div className="mt-[var(--space-5)]">
          <ol
            ref={timelineRef}
            data-ready={timelineReady}
            data-visible={timelineVisible}
            className="thl-process-timeline relative flex flex-col gap-10 border-l border-[var(--border)] pl-8 lg:flex-row lg:gap-0 lg:border-l-0 lg:border-t lg:pl-0 lg:pt-10"
          >
            {methodChapter.steps.map((step) => (
              <li
                key={step.num}
                className="thl-process-step relative lg:flex-1 lg:border-l lg:border-[var(--border)] lg:px-6 lg:first:border-l-0 lg:first:pl-0"
                style={{ "--step-index": Number(step.num) - 1 } as React.CSSProperties}
              >
                <span className="text-caption text-[var(--accent)]">
                  {step.num}
                </span>
                <h3 className="text-heading mt-3 text-[var(--text-primary)]">
                  {step.title}
                </h3>
                <p className="text-body mt-3 text-[var(--text-secondary)]">
                  {step.text}
                </p>
              </li>
            ))}
          </ol>
          <p className="text-body mt-[var(--space-4)] text-[var(--text-muted)]">
            {methodChapter.note}
          </p>
        </div>

        <div className="mt-20 border-t border-thl-border pt-16">
          <h3 className="text-lg font-medium md:text-xl">{methodChapter.principlesTitle}</h3>
          <ol className="mt-10 flex flex-col divide-y divide-thl-border xl:flex-row xl:divide-x xl:divide-y-0">
            {methodChapter.principles.map((principle) => (
              <li key={principle.num} className="flex gap-4 py-8 first:pt-0 xl:flex-1 xl:flex-col xl:px-8 xl:first:pl-0 xl:last:pr-0">
                <span className="font-mono text-sm text-thl-text-muted">{principle.num}</span>
                <div>
                  <p className="text-base font-semibold md:text-lg">{principle.title}</p>
                  <p className="mt-2 text-sm leading-relaxed text-thl-text-secondary md:text-base">
                    {principle.text}
                  </p>
                </div>
              </li>
            ))}
          </ol>
          <div className="mt-12">
            <CtaLink href={ROUTES.quote} variant="outline">
              {methodChapter.cta}
            </CtaLink>
          </div>
        </div>
      </div>
      <style jsx global>{`
        .thl-process-step::before {
          position: absolute;
          width: 8px;
          height: 8px;
          border-radius: 9999px;
          background: var(--accent);
          content: "";
        }

        .thl-process-step::before {
          top: 0;
          left: -36px;
        }

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

        @media (min-width: 1024px) {
          .thl-process-step::before {
            top: -14px;
            left: 24px;
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
