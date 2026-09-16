import { homeContent } from "@/lib/content/home";
import { ServiceIcon } from "@/components/home/service-icon";

export function ServicesSection() {
  const { services } = homeContent;

  return (
    <section
      id="services"
      aria-labelledby="services-heading"
      className="bg-[var(--bg-primary)] py-[var(--space-6)]"
    >
      <div className="thl-container">
        <p className="text-caption text-[var(--text-muted)]">{services.eyebrow}</p>
        <h2 id="services-heading" className="text-display-m mt-4 text-[var(--text-primary)]">
          {services.title}
        </h2>
        <ul className="mt-[var(--space-5)] grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-2">
          {services.items.map((item) => (
            <li key={item.id}>
              <article className="group flex min-h-64 flex-col border border-[var(--border)] bg-[var(--bg-elevated)] p-[var(--space-4)] transition-[border-color,transform] duration-[var(--duration-fast)] ease-[var(--ease-lux)] hover:-translate-y-0.5 hover:border-[var(--border-strong)]">
                <div className="text-[var(--accent)]">
                  <ServiceIcon name={item.icon} />
                </div>
                <h3 className="mt-[var(--space-5)] text-heading text-[var(--text-primary)]">
                  {item.title}
                </h3>
                <p className="mt-[var(--space-3)] text-body text-[var(--text-secondary)]">
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
