import { homeContent } from "@/lib/content/home";

export function VisionSection() {
  const { vision } = homeContent;

  return (
    <section
      aria-labelledby="vision-heading"
      className="bg-[var(--bg-secondary)] py-[var(--space-6)]"
    >
      <div className="thl-container">
        <div className="max-w-3xl">
          <p className="text-caption text-[var(--text-muted)]">{vision.eyebrow}</p>
          <h2 id="vision-heading" className="text-display-m mt-4 text-[var(--text-primary)]">
            {vision.title}
          </h2>
          <p className="text-body-l mt-[var(--space-4)] text-[var(--text-secondary)]">
            {vision.body}
          </p>
        </div>
      </div>
    </section>
  );
}
