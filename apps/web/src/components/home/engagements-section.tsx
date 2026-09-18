import Image from "next/image";
import { homeContent } from "@/lib/content/home";

const BACKGROUND = "/images/engagements/engagements.jpg";

export function EngagementsSection() {
  const { engagements } = homeContent;

  return (
    <section
      aria-labelledby="engagements-heading"
      className="relative isolate overflow-hidden py-[var(--space-6)] lg:py-[var(--space-7)]"
    >
      <Image
        src={BACKGROUND}
        alt=""
        aria-hidden
        fill
        sizes="100vw"
        className="object-cover object-center"
      />
      {/* Vertical anchoring into the page background, then a global veil for legibility. */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "linear-gradient(180deg, rgba(10,10,10,0.9) 0%, rgba(10,10,10,0.34) 22%, rgba(10,10,10,0.34) 78%, rgba(10,10,10,0.9) 100%), rgba(10,10,10,0.72)",
        }}
      />
      <div className="relative z-10">
        <div className="thl-container">
          {/* text-secondary, not text-muted: 14px muted never reaches 4.5:1 over a photo. */}
          <p className="text-caption text-[var(--text-secondary)]">{engagements.eyebrow}</p>
          <h2
            id="engagements-heading"
            className="text-display-m mt-4 text-[var(--text-primary)]"
          >
            {engagements.title}
          </h2>
          <ul className="mt-[var(--space-5)] grid grid-cols-1 gap-[var(--space-5)] lg:grid-cols-3">
            {engagements.items.map((item) => (
              <li key={item.title} className="border-l-2 border-[var(--accent)] pl-[var(--space-4)]">
                <article>
                  <h3 className="text-heading text-[var(--text-primary)]">{item.title}</h3>
                  <p className="text-body mt-[var(--space-3)] text-[var(--text-secondary)]">
                    {item.description}
                  </p>
                </article>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
