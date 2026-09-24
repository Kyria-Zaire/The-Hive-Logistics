import Image from "next/image";
import { ArrowRight } from "lucide-react";

type ServiceCardItem = {
  id: string;
  title: string;
  description: string;
  image: string;
};

type ServiceCardProps = {
  item: ServiceCardItem;
  /** Tablet: this tile spans both columns, where a 2:3 ratio would make it ~960px tall. */
  wide?: boolean;
};

/** Full-bleed portrait tile, shared by the home section and the /services page. */
export function ServiceCard({ item, wide = false }: ServiceCardProps) {
  const headingId = `service-${item.id}`;

  return (
    <article
      aria-labelledby={headingId}
      // mx-auto: on short viewports the 80vh cap narrows the tile, which must stay centred in its cell.
      className={`thl-tile group relative mx-auto aspect-[2/3] overflow-hidden rounded-[var(--radius)] lg:max-h-[min(80vh,720px)] ${
        wide ? "md:aspect-[3/2] lg:aspect-[2/3]" : ""
      }`.trim()}
    >
      <Image
        src={item.image}
        alt=""
        aria-hidden
        fill
        sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
        className="thl-tile-image object-cover object-center"
      />
      <div
        aria-hidden
        className="absolute inset-0"
        style={{
          background:
            // Full opacity, bottom stop 0.93: the portrait crop puts brighter pixels behind the
            // 16px description, which needs 4.5:1 — measured at 4.96:1 on the third tile.
            "linear-gradient(180deg, rgba(10,10,10,0.15) 0%, rgba(10,10,10,0.55) 50%, rgba(10,10,10,0.93) 100%)",
        }}
      />
      <div className="absolute inset-x-0 bottom-0 p-[var(--space-4)] lg:p-[var(--space-5)]">
        <h3
          id={headingId}
          className="text-heading flex items-start justify-between gap-3 uppercase tracking-[0.12em] text-[var(--text-primary)]"
        >
          {/* Title and arrow step aside together on hover, each on its own element: moving the
              heading itself would have carried the arrow with it and doubled its travel.
              Transform only, so neither reflows the tile — and neither moves at all under
              reduced motion, where the transition is dropped as well. */}
          <span className="block transition-transform duration-[400ms] ease-[var(--ease-lux)] group-hover:translate-x-1 motion-reduce:transition-none motion-reduce:group-hover:translate-x-0">
            {item.title}
          </span>
          <ArrowRight
            aria-hidden
            strokeWidth={1.5}
            className="mt-[0.3em] size-6 shrink-0 text-[var(--text-secondary)] transition-transform duration-[400ms] ease-[var(--ease-lux)] group-hover:translate-x-1 motion-reduce:transition-none motion-reduce:group-hover:translate-x-0"
          />
        </h3>
        <p className="mt-[var(--space-3)] text-body line-clamp-2 text-[var(--text-secondary)]">
          {item.description}
        </p>
      </div>
    </article>
  );
}
