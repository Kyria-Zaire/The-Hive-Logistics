import { homeContent } from "@/lib/content/home";

export function VisionSection() {
  const { vision } = homeContent;

  return (
    <section aria-labelledby="vision-heading" className="bg-thl-bg-deep py-12 md:py-16">
      <div className="thl-container">
        <div className="max-w-[680px]">
          <h2 id="vision-heading" className="text-2xl font-semibold md:text-3xl">
            {vision.title}
          </h2>
          <p className="mt-6 text-base leading-relaxed text-thl-text-secondary md:text-lg">
            {vision.body}
          </p>
        </div>
      </div>
    </section>
  );
}
