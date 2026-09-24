import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";
import { CtaLink } from "@/components/ui/cta-link";

export function ConversionSection() {
  const { conversion } = homeContent;

  return (
    <section
      aria-labelledby="conversion-heading"
      className="section-light py-16 md:py-20"
    >
      <div className="thl-container">
        <div className="mx-auto max-w-[720px] text-center">
          <h2 id="conversion-heading" className="text-2xl font-semibold md:text-3xl">
            {conversion.title}
          </h2>
          <p className="mt-4 text-base text-[var(--text-dark-secondary)] md:text-lg">
            {conversion.body}
          </p>
          <div className="mx-auto mt-8 flex max-w-[360px] flex-col gap-3 sm:max-w-none sm:flex-row sm:justify-center">
            <CtaLink href={ROUTES.quote} variant="outline" className="w-full sm:w-auto">
              {conversion.ctaPrimary}
            </CtaLink>
            <CtaLink href={ROUTES.contact} variant="outline" className="w-full sm:w-auto">
              {conversion.ctaSecondary}
            </CtaLink>
          </div>
        </div>
      </div>
    </section>
  );
}
