import Image from "next/image";
import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";
import { CtaLink } from "@/components/ui/cta-link";
import { MethodRoad } from "@/components/home/method-road";
// Client Component imported from a Server Component: Next code-splits it per route, so GSAP
// ships with "/" only. `next/dynamic` with `ssr: false` is rejected here — see TICKET 20 report.
import { MethodAnimated } from "@/components/home/method-animated";

// Renamed with the asset: the optimiser caches by URL, so replacing the file in place kept
// serving the previous car.
const CAR = "/images/method/car-method-red.png";

/** A different model for the second scene, so the two crossings do not read as one loop. */
const PRINCIPLES_CAR = "/images/method/car-principles-911.png";

/** Pure black, not --bg-primary: keeps the night composition of the reference. */
const NIGHT = "#000000";

/**
 * Layers, bottom to top: the pinned screen carrying the road and the steps (z-10), the note
 * the car drives across (z-20), the car on its own pinned layer (z-30), and the opaque block
 * that swallows the car at the separator line (z-40). The car needs to paint over the note
 * while the road must not — a white marking behind that 16px text measured 1.30:1 — hence the
 * two pinned layers rather than one.
 */
export function MethodChapterSection() {
  const { methodChapter } = homeContent;

  return (
    <section
      aria-labelledby="methode-hive"
      // isolate: keeps this section's stacking to itself, so the section above can paint over
      // the car while it is still above the boundary between the two.
      className="section-dark relative isolate"
      // clip-path, not overflow: overflow would make this a scroll container and break the
      // sticky screens inside. This confines the car to its own section — sent above the top
      // boundary for its entrance, it was showing up in the sections further up the page.
      style={{ backgroundColor: NIGHT, clipPath: "inset(0)" }}
    >
      {/* Scroll track: the pinned screens need their own height to travel through, otherwise
          the principles below slide over them after a single screen instead of three. */}
      <div className="thl-method-scroll relative h-[280vh] lg:h-[320vh]">
        <div className="sticky top-0 z-10 h-screen">
          {/* Scrim: the car passes behind the title, which measured 1.15:1 without it.
              Solid down to the title's baseline, then faded out. */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-0 top-0 z-30 h-[210px] lg:h-[300px]"
            style={{
              background: `linear-gradient(180deg, ${NIGHT} 0%, ${NIGHT} 62%, transparent 100%)`,
            }}
          />

          <div className="thl-container absolute inset-x-0 top-16 z-40 lg:top-20">
            <p className="text-caption text-[var(--text-secondary)]">{methodChapter.eyebrow}</p>
            <h2 id="methode-hive" className="text-display-m mt-4 text-[var(--text-primary)]">
              {methodChapter.chapterTitle}
            </h2>
          </div>

          {/* Runs past the bottom of the pinned screen: its own edge was appearing mid-page when
              the screen was released. The overshoot ends behind the opaque block below. */}
          <MethodRoad className="absolute left-[22%] top-0 h-[calc(100%+420px)] w-1.5 -translate-x-1/2 lg:left-1/2" />

          {/* A window the step column travels through, faded at both edges so steps dissolve as
              they leave rather than being cut off. */}
          <div className="thl-method-steps absolute bottom-0 left-[46%] right-[var(--container-padding)] top-[190px] z-20 flex items-center overflow-hidden md:left-[38%] md:top-[230px] lg:left-auto lg:right-[7%] lg:top-0 lg:w-[34%]">
            {/* Two gradients in the section's own black rather than a CSS mask: an alpha mask
                had to be recomposited on every frame and cost ~10 fps on the pinned screen. */}
            <span
              aria-hidden
              className="pointer-events-none absolute inset-x-0 top-0 z-20 h-[14%]"
              style={{ background: `linear-gradient(180deg, ${NIGHT} 0%, transparent 100%)` }}
            />
            <span
              aria-hidden
              className="pointer-events-none absolute inset-x-0 bottom-0 z-20 h-[14%]"
              style={{ background: `linear-gradient(0deg, ${NIGHT} 0%, transparent 100%)` }}
            />
            <ol
              style={{ willChange: "transform" }}
              className="thl-method-list relative z-10 flex w-full flex-col gap-[var(--space-6)] lg:gap-[var(--space-7)]"
            >
              {methodChapter.steps.map((step) => (
                <li
                  key={step.num}
                  // Narrow screens stack: a 96px number beside a spaced-out uppercase label does
                  // not fit 390px, and the label ran off the right edge.
                  className="thl-method-step flex flex-col gap-[var(--space-3)] lg:flex-row lg:items-start lg:gap-[var(--space-4)]"
                  data-step={step.num}
                >
                  <span className="thl-method-number block shrink-0 text-[40px] font-light leading-none text-[var(--text-primary)] md:text-[52px] lg:text-[96px]">
                    {step.num}
                  </span>
                  <div className="lg:pt-2">
                    <h3 className="text-[20px] font-medium uppercase leading-tight tracking-[0.12em] text-[var(--text-primary)] md:text-[24px] lg:text-heading">
                      {step.title}
                    </h3>
                    <p className="text-body mt-[var(--space-3)] text-[var(--text-secondary)]">
                      {step.text}
                    </p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </div>

        {/* The car has its own pinned layer, pulled back over the first one, so it can paint
            above the note while the road and the steps stay below it. */}
        <div className="thl-method-car-layer pointer-events-none sticky top-0 z-30 -mt-[100vh] h-screen">
          <div className="absolute left-[22%] top-[46%] -translate-x-1/2 -translate-y-1/2 lg:left-1/2 lg:top-[62%]">
            {/* Carriage: the pinned timeline drives the car's own transform, so the run down to
                the separator gets its own element instead of fighting over the same property. */}
            <span className="thl-method-approach block">
              <span className="thl-method-carriage block">
                <Image
                  src={CAR}
                  alt=""
                  aria-hidden
                  width={1024}
                  height={1536}
                  sizes="(min-width: 1024px) 280px, (min-width: 768px) 26vw, 34vw"
                  className="thl-method-car block w-[34vw] max-w-[190px] md:w-[26vw] md:max-w-[240px] lg:w-[280px] lg:max-w-none"
                />
              </span>
            </span>
          </div>
        </div>
      </div>

      {/* Between the pinned screens and the line: the car drives across this text. */}
      <div className="relative z-20 pt-[var(--space-6)] lg:pt-[var(--space-7)]">
        <div className="thl-container">
          {/* Its own black behind it: this text sits above the road, and a white marking
              showing through these 16px glyphs measured 1.71:1. The car still drives over it —
              it is on the layer above. */}
          <p
            className="text-body max-w-2xl py-[var(--space-3)] text-[var(--text-secondary)]"
            style={{ backgroundColor: NIGHT }}
          >
            {methodChapter.note}
          </p>
        </div>
      </div>

      {/* Opaque from the separator down: this is what swallows the car. */}
      <div
        // The separator sits on this full-width block, not inside the container, so it runs
        // from one edge of the screen to the other.
        className="relative z-40 mt-[var(--space-6)] border-t border-[var(--border)]"
        style={{ backgroundColor: NIGHT }}
      >
        {/* Still the trigger for the car's dive: the timeline reads this element's top. */}
        <div className="thl-method-line">
          {/* The principles get the same staging turned on its side: the road runs across, and
              the car drives it from one edge of the screen to the other. */}
          <div className="thl-principles-scroll relative h-[200vh] lg:h-[220vh]">
            <div className="sticky top-0 h-screen overflow-hidden">
              <div className="thl-container absolute inset-x-0 top-20 lg:top-24">
                <h3 className="text-display-m text-[var(--text-primary)]">
                  {methodChapter.principlesTitle}
                </h3>
              </div>

              <MethodRoad
                orientation="horizontal"
                className="absolute inset-x-0 top-[34%] h-1.5 lg:top-[46%]"
              />

              {/* A quarter turn anti-clockwise: the photograph is shot nose-up, and turning it
                  the other way put the bonnet on the left — the car crossed the screen in
                  reverse. The animation reads the image's own box, transform included, to know
                  when it has really cleared each edge of the screen. */}
              {/* Two elements rather than one: the outer div places the car on the road and
                  keeps Tailwind's `translate`, the inner span carries nothing but the
                  crossing. GSAP folds an element's `translate` into the transform it drives,
                  and the tween then overwrote the -50% centring — the car entered the screen
                  62px short of the edge. At rest (reduced motion, or before the timeline
                  runs) it simply sits in the middle of the road. */}
              <div className="absolute left-1/2 top-[34%] -translate-x-1/2 -translate-y-1/2 lg:top-[46%]">
                <span className="thl-principles-car block">
                  <Image
                    src={PRINCIPLES_CAR}
                    alt=""
                    aria-hidden
                    width={1024}
                    height={1536}
                    sizes="(min-width: 1024px) 260px, (min-width: 768px) 24vw, 32vw"
                    className="thl-principles-car-body block w-[32vw] max-w-[180px] -rotate-90 md:w-[24vw] md:max-w-[220px] lg:w-[260px] lg:max-w-none"
                  />
                </span>
              </div>

              <div className="thl-container absolute inset-x-0 bottom-[8%] lg:bottom-[14%]">
                <ol className="grid grid-cols-2 gap-[var(--space-4)] md:gap-[var(--space-5)] lg:grid-cols-4">
                  {methodChapter.principles.map((principle) => (
                    <li key={principle.num} className="thl-principle">
                      <span className="text-caption text-[var(--text-secondary)]">
                        {principle.num}
                      </span>
                      <p className="mt-[var(--space-3)] text-[17px] font-medium leading-snug text-[var(--text-primary)] md:text-[22px] lg:text-heading">
                        {principle.title}
                      </p>
                      <p className="mt-[var(--space-3)] text-[14px] leading-relaxed text-[var(--text-secondary)] md:text-body">
                        {principle.text}
                      </p>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          </div>

          <div className="thl-container pb-[var(--space-6)] lg:pb-[var(--space-7)]">
            <CtaLink href={ROUTES.quote} variant="outline">
              {methodChapter.cta}
            </CtaLink>
          </div>
        </div>
      </div>
      <MethodAnimated />
    </section>
  );
}
