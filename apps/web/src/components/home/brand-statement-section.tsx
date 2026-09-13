import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";
import { TextLink } from "@/components/ui/text-link";

export function BrandStatementSection() {
  const { brandStatement } = homeContent;

  return (
    <section
      aria-labelledby="brand-statement-heading"
      className="bg-thl-bg-deep py-16 md:py-20"
    >
      <div className="thl-container">
        <div className="max-w-[680px] border-l-4 border-thl-accent pl-6 md:pl-8">
          <h2
            id="brand-statement-heading"
            className="text-2xl font-semibold leading-tight md:text-3xl xl:text-4xl"
          >
            {brandStatement.title}
          </h2>
          <p className="mt-6 text-base leading-relaxed text-thl-text-secondary md:text-lg">
            {brandStatement.body}
          </p>
          <div className="mt-8">
            <TextLink href={ROUTES.about}>{brandStatement.linkLabel}</TextLink>
          </div>
        </div>
      </div>
    </section>
  );
}
