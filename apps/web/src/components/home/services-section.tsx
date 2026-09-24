import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";
// Client Components imported from a Server Component: Next code-splits them per route, so GSAP
// ships with "/" only. `next/dynamic` with `ssr: false` is rejected here — see TICKET 20 report.
import { AccordionGallery } from "@/components/home/accordion-gallery";
import { ServicesAnimated } from "@/components/home/services-animated";

export function ServicesSection() {
  const { services } = homeContent;

  const panels = services.items.map((item) => ({
    image: item.image,
    label: item.title,
    description: item.description,
    link: ROUTES.contact,
  }));

  return (
    <section
      id="services"
      aria-labelledby="services-heading"
      className="section-light py-[var(--space-6)] lg:py-[var(--space-7)]"
    >
      <div className="thl-container">
        <p className="text-caption text-[var(--text-dark-muted)]">{services.eyebrow}</p>
        <h2 id="services-heading" className="text-display-m mt-4 text-[var(--text-dark-primary)]">
          {services.title}
        </h2>
        <div className="mt-[var(--space-5)]">
          <AccordionGallery
            items={panels}
            label={services.title}
            defaultIndex={0}
            expandRatio={0.52}
            trigger="hover"
            accentColor="#DC2626"
            overlayColor="#0A0A0A"
            textColor="#FFFFFF"
            grayscale
            showLabels
            duration={0.6}
            ease="power3.out"
            parallax={0.5}
            tilt={8}
            stagger={0.06}
            height={460}
            gap={10}
            radius={16}
            orientation="horizontal"
          />
        </div>
      </div>
      <ServicesAnimated />
    </section>
  );
}
