import { homeContent } from "@/lib/content/home";

export function EngagementsSection() {
  const { engagements } = homeContent;

  return (
    <section
      aria-labelledby="engagements-heading"
      className="bg-[var(--bg-secondary)] py-[var(--space-6)]"
    >
      <div className="thl-container">
        <p className="text-caption text-[var(--text-muted)]">{engagements.eyebrow}</p>
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
    </section>
  );
}