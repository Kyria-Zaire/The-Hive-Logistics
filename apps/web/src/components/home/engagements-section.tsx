import Image from "next/image";
import { homeContent } from "@/lib/content/home";
// Client Component imported from a Server Component: Next code-splits it per route, so GSAP
// ships with "/" only. `next/dynamic` with `ssr: false` is rejected here — see TICKET 20 report.
import { EngagementsAnimated } from "@/components/home/engagements-animated";

const BACKGROUND = "/images/engagements/engagements.jpg";

/**
 * TICKET 23-BIS — the backdrop opens from a card to the full screen while the screen is
 * pinned, the heading hands over to the three commitments, and the photograph zooms back to
 * its natural scale.
 *
 * Everything is in the HTML: the heading, the three commitments and the photograph are
 * server-rendered and opaque. The client component only takes them through the opening.
 * Under reduced motion the `motion-reduce:` variants below unpin the whole thing and lay it
 * out as a plain stack — heading, photograph, commitments — with no timeline built at all.
 */
export function EngagementsSection() {
  const { engagements } = homeContent;

  return (
    <section
      aria-labelledby="engagements-heading"
      // No overflow-hidden here: it would make this a scroll container and kill the sticky
      // stage inside. The stage clips its own overflow instead.
      className="section-dark relative isolate"
    >
      {/* Height per breakpoint, and the unpinned one, live in globals.css: as utilities they
          all tied on specificity and `lg:` beat `motion-reduce:`. */}
      <div className="thl-engagements-track relative">
        <div className="thl-engagements-stage sticky top-0 h-screen overflow-hidden motion-reduce:static motion-reduce:h-auto motion-reduce:overflow-visible motion-reduce:py-[var(--space-6)]">
          {/* The frame: clip-path comes from globals.css, one opening per breakpoint. */}
          <div className="thl-engagements-frame absolute inset-0 motion-reduce:relative motion-reduce:inset-auto motion-reduce:h-[60vh]">
            <Image
              src={BACKGROUND}
              alt=""
              aria-hidden
              fill
              sizes="100vw"
              // 80, not 60: the photograph used to sit under a 0.72 veil where detail was
              // wasted. It is the subject now, and it ends the scroll at full bleed.
              quality={80}
              className="thl-engagements-media object-cover object-center"
            />
            {/* Scrim inside the frame so it opens with it, rather than a veil over the whole
                stage that would sit on the black margins too. It is what carries the heading
                and the commitments to their contrast thresholds. */}
            <div
              aria-hidden
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "linear-gradient(180deg, rgba(10,10,10,0.6) 0%, rgba(10,10,10,0.38) 45%, rgba(10,10,10,0.78) 100%), rgba(10,10,10,0.4)",
              }}
            />
          </div>

          {/* Heading: centred in the frame at the start, gone by the time it is full bleed. */}
          <div className="thl-engagements-title absolute inset-0 z-10 flex flex-col items-center justify-center px-[var(--container-padding)] text-center motion-reduce:static motion-reduce:mt-[var(--space-5)] motion-reduce:h-auto">
            {/* White, not the secondary grey: at 14px this line needs 4.5:1, and over the
                photograph the grey measured 1.88:1. Holding it with the scrim instead would
                mean taking the backdrop down to a luminance of 0.04 — a black rectangle, which
                is the opposite of what opening the frame is for. */}
            <p className="text-caption text-[var(--text-primary)]">{engagements.eyebrow}</p>
            <h2
              id="engagements-heading"
              className="text-display-m mt-4 max-w-4xl text-[var(--text-primary)]"
            >
              {engagements.title}
            </h2>
          </div>

          {/* The three commitments, stacked and centred — they arrive once the frame is open. */}
          <div className="thl-engagements-overlay absolute inset-0 z-10 flex items-center justify-center px-[var(--container-padding)] motion-reduce:static motion-reduce:mt-[var(--space-5)] motion-reduce:h-auto">
            <ul className="mx-auto flex max-w-3xl flex-col gap-[var(--space-5)] text-center">
              {engagements.items.map((item) => (
                <li key={item.title} className="thl-engagement">
                  <h3 className="text-heading text-[var(--text-primary)]">{item.title}</h3>
                  {/* Same reason as the eyebrow: 16px over a photograph needs 4.5:1, which the
                      secondary grey reached at 1.79:1 here. */}
                  <p className="text-body mt-[var(--space-3)] text-[var(--text-primary)]">
                    {item.description}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      <EngagementsAnimated />
    </section>
  );
}
