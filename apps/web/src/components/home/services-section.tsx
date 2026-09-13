import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";
import { TextLink } from "@/components/ui/text-link";
import { ServiceMediaFrame } from "@/components/home/service-media-frame";

export function ServicesSection() {
  const { services } = homeContent;

  return (
    <section
      id="services"
      aria-labelledby="services-heading"
      className="bg-thl-bg-deep py-20 md:py-24"
    >
      <div className="thl-container">
        <h2 id="services-heading" className="text-2xl font-semibold md:text-3xl xl:text-4xl">
          {services.title}
        </h2>
        <ul className="mt-16 flex flex-col gap-12 lg:gap-24">
          {services.items.map((item, index) => {
            const reversed = index % 2 === 1;
            return (
              <li key={item.id}>
                <article
                  className={`grid grid-cols-1 items-start gap-8 lg:grid-cols-12 lg:gap-8 ${
                    reversed ? "lg:[&>*:first-child]:order-2" : ""
                  } ${index % 2 === 1 ? "lg:translate-y-6" : ""}`}
                >
                  <div className="lg:col-span-5">
                    <ServiceMediaFrame />
                  </div>
                  <div className="lg:col-span-7 lg:pt-4">
                    <p className="text-xs uppercase tracking-[0.08em] text-thl-text-muted">
                      {item.need}
                    </p>
                    <h3 className="mt-2 text-xl font-semibold md:text-2xl">{item.title}</h3>
                    <p className="mt-4 text-base leading-relaxed text-thl-text-secondary">
                      {item.description}
                    </p>
                  </div>
                </article>
              </li>
            );
          })}
        </ul>
        <div className="mt-16">
          <TextLink href={ROUTES.services}>{services.cta}</TextLink>
        </div>
      </div>
    </section>
  );
}
