import { homeContent } from "@/lib/content/home";
import { ROUTES } from "@/lib/routes";
import { CtaLink } from "@/components/ui/cta-link";

export function MethodChapterSection() {
  const { methodChapter } = homeContent;

  return (
    <section
      aria-labelledby="methode-hive"
      className="bg-thl-bg-elevated py-20 md:py-28 xl:py-32"
    >
      <div className="thl-container thl-chapter-enter">
        <h2 id="methode-hive" className="text-2xl font-semibold md:text-3xl xl:text-4xl">
          {methodChapter.chapterTitle}
        </h2>

        <div className="mt-16">
          <h3 className="text-lg font-medium text-thl-text-secondary md:text-xl">
            {methodChapter.processTitle}
          </h3>
          <ol className="relative mt-10 flex flex-col gap-10 border-l border-thl-border pl-8 xl:flex-row xl:gap-0 xl:border-l-0 xl:border-t xl:pl-0 xl:pt-10">
            {methodChapter.steps.map((step) => (
              <li
                key={step.num}
                className="relative xl:flex-1 xl:border-l xl:border-thl-border xl:px-6 xl:first:border-l-0 xl:first:pl-0"
              >
                <span className="absolute -left-[2.125rem] top-0 font-mono text-sm text-thl-text-muted xl:static xl:mb-4 xl:block">
                  {step.num}
                </span>
                <p className="text-lg font-semibold">{step.title}</p>
                <p className="mt-2 text-sm leading-relaxed text-thl-text-secondary md:text-base">
                  {step.text}
                </p>
              </li>
            ))}
          </ol>
          <p className="mt-10 text-sm italic text-thl-text-muted">{methodChapter.note}</p>
        </div>

        <div className="mt-20 border-t border-thl-border pt-16">
          <h3 className="text-lg font-medium md:text-xl">{methodChapter.principlesTitle}</h3>
          <ol className="mt-10 flex flex-col divide-y divide-thl-border xl:flex-row xl:divide-x xl:divide-y-0">
            {methodChapter.principles.map((principle) => (
              <li key={principle.num} className="flex gap-4 py-8 first:pt-0 xl:flex-1 xl:flex-col xl:px-8 xl:first:pl-0 xl:last:pr-0">
                <span className="font-mono text-sm text-thl-text-muted">{principle.num}</span>
                <div>
                  <p className="text-base font-semibold md:text-lg">{principle.title}</p>
                  <p className="mt-2 text-sm leading-relaxed text-thl-text-secondary md:text-base">
                    {principle.text}
                  </p>
                </div>
              </li>
            ))}
          </ol>
          <div className="mt-12">
            <CtaLink href={ROUTES.quote} variant="outline">
              {methodChapter.cta}
            </CtaLink>
          </div>
        </div>
      </div>
    </section>
  );
}
