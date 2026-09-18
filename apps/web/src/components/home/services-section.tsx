import { homeContent } from "@/lib/content/home";
import { ServiceCard } from "@/components/home/service-card";

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
        <ul className="mt-[var(--space-5)] grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {services.items.map((item, index) => (
            <li
              key={item.id}
              // Odd card out: full width on the 2-column tablet grid, plain column at lg.
              className={
                index === services.items.length - 1 ? "md:col-span-2 lg:col-span-1" : undefined
              }
            >
              <ServiceCard item={item} />
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
