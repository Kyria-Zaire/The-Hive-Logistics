import Image from "next/image";

type ServiceCardItem = {
  id: string;
  title: string;
  description: string;
  image: string;
};

/** Full-bleed image card, shared by the home section and the /services page. */
export function ServiceCard({ item }: { item: ServiceCardItem }) {
  const headingId = `service-${item.id}`;

  return (
    <article
      aria-labelledby={headingId}
      className="group relative h-[380px] overflow-hidden rounded-[var(--radius)] md:h-[480px]"
    >
      <Image
        src={item.image}
        alt=""
        aria-hidden
        fill
        sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
        className="object-cover object-center transition-transform duration-[600ms] ease-[var(--ease-lux)] group-hover:scale-105 motion-reduce:transition-none motion-reduce:group-hover:scale-100"
      />
      <div
        className="absolute inset-0 opacity-90 transition-opacity duration-[600ms] ease-[var(--ease-lux)] group-hover:opacity-100 motion-reduce:transition-none"
        style={{
          background:
            // Bottom stop raised 0.90 -> 0.93: the 16px description needs 4.5:1 over the image.
            "linear-gradient(180deg, rgba(10,10,10,0.15) 0%, rgba(10,10,10,0.55) 50%, rgba(10,10,10,0.93) 100%)",
        }}
      />
      <div className="absolute inset-x-0 bottom-0 p-[var(--space-4)] lg:p-[var(--space-5)]">
        <h3 id={headingId} className="text-heading text-[var(--text-primary)]">
          {item.title}
        </h3>
        <p className="mt-[var(--space-3)] text-body text-[var(--text-secondary)]">
          {item.description}
        </p>
      </div>
    </article>
  );
}
