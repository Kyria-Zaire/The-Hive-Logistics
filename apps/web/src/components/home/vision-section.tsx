import type { ReactNode } from "react";
import Image from "next/image";
import { homeContent } from "@/lib/content/home";

const BACKGROUND = "/images/vision/vision-bg.jpg";

type VisionSectionProps = {
  /**
   * The scroll animation, passed in rather than imported here. That import is what would pull
   * GSAP into every route rendering this section: /a-propos shows the same statement and has
   * no use for the animation, and picking it up cost that page 114 Ko and a 1800px track.
   * Given nothing, the section lays itself out as a plain block.
   */
  animation?: ReactNode;
};

/**
 * TICKET 24 — the statement is read out word by word as the screen is scrolled past it.
 *
 * The split happens here, on the server: the sentence is in the HTML, whole, with its spaces
 * between the spans. Splitting it on the client would have meant shipping the paragraph as one
 * string and cutting it after hydration — fine for the eye, poor for a crawler and for anyone
 * copying the text out.
 */
export function VisionSection({ animation }: VisionSectionProps) {
  const { vision } = homeContent;
  // Capturing split: the separators come back in the array, so the spaces survive between the
  // spans. Without them the sentence reads as one unbroken word to a screen reader.
  const pieces = vision.body.split(/(\s+)/);
  const animated = Boolean(animation);

  return (
    <section
      aria-labelledby="vision-heading"
      // No overflow-hidden on the section: it would make this a scroll container and kill the
      // sticky stage. The stage clips its own overflow instead.
      className="section-dark relative isolate"
    >
      {/* Height per breakpoint, and the unpinned one, live in globals.css. Without the
          animation there is nothing to scrub through, so the track is not one. */}
      <div className={animated ? "thl-vision-track relative" : "relative"}>
        <div
          className={
            animated
              ? "thl-vision-stage sticky top-0 h-screen overflow-hidden motion-reduce:static motion-reduce:h-auto motion-reduce:overflow-visible motion-reduce:py-[var(--space-7)]"
              : "relative py-[var(--space-7)] lg:py-[200px]"
          }
        >
          <Image
            src={BACKGROUND}
            alt=""
            aria-hidden
            fill
            sizes="100vw"
            quality={60}
            className="object-cover object-[center_85%]"
          />
          {/* Vertical anchoring into the page background, then a global veil for legibility. */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0"
            style={{
              background:
                "linear-gradient(180deg, rgba(10,10,10,0.85) 0%, rgba(10,10,10,0.31) 25%, rgba(10,10,10,0.31) 75%, rgba(10,10,10,0.85) 100%), rgba(10,10,10,0.73)",
            }}
          />

          <div
            className={
              animated
                ? "relative z-10 flex h-full items-center motion-reduce:h-auto"
                : "relative z-10"
            }
          >
            <div className="thl-container">
              {/* Centred, unlike the factual Engagements block: this one reads as a statement. */}
              <div className="mx-auto max-w-3xl text-center">
                <div className="thl-vision-intro">
                  <p className="text-caption text-[var(--text-secondary)]">{vision.eyebrow}</p>
                  <h2
                    id="vision-heading"
                    className="text-display-m mt-4 text-[var(--text-primary)]"
                  >
                    {vision.title}
                  </h2>
                </div>
                <p className="thl-vision-body text-body-l mx-auto mt-[var(--space-4)] max-w-2xl text-[var(--text-secondary)]">
                  {pieces.map((piece, index) =>
                    /^\s+$/.test(piece) ? (
                      piece
                    ) : (
                      // Index as key: the sentence is static content, its words never reorder,
                      // and two identical words would collide on a text key.
                      <span key={index} className="word">
                        {piece}
                      </span>
                    ),
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      {animation}
    </section>
  );
}
