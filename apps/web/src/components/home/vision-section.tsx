import Image from "next/image";
import { homeContent } from "@/lib/content/home";

const BACKGROUND = "/images/vision/vision-bg.jpg";

export function VisionSection() {
  const { vision } = homeContent;

  return (
    <section
      aria-labelledby="vision-heading"
      className="relative isolate overflow-hidden py-[var(--space-7)] lg:py-[200px]"
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
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "linear-gradient(180deg, rgba(10,10,10,0.85) 0%, rgba(10,10,10,0.31) 25%, rgba(10,10,10,0.31) 75%, rgba(10,10,10,0.85) 100%), rgba(10,10,10,0.73)",
        }}
      />
      <div className="relative z-10">
        <div className="thl-container">
          {/* Centred, unlike the factual Engagements block: this one reads as a statement. */}
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-caption text-[var(--text-secondary)]">{vision.eyebrow}</p>
            <h2 id="vision-heading" className="text-display-m mt-4 text-[var(--text-primary)]">
              {vision.title}
            </h2>
            <p className="text-body-l mx-auto mt-[var(--space-4)] max-w-2xl text-[var(--text-secondary)]">
              {vision.body}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
