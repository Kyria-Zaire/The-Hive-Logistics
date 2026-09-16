import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { HeroSection } from "@/components/home/hero-section";
import { BrandStatementSection } from "@/components/home/brand-statement-section";
import { ServicesSection } from "@/components/home/services-section";
import { EngagementsSection } from "@/components/home/engagements-section";
import { MethodChapterSection } from "@/components/home/method-chapter-section";
import { VisionSection } from "@/components/home/vision-section";
import { ConversionSection } from "@/components/home/conversion-section";
export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="flex flex-1 flex-col">
        <HeroSection />
        <BrandStatementSection />
        <ServicesSection />
        <EngagementsSection />
        <MethodChapterSection />
        <VisionSection />
        <ConversionSection />
      </main>
      <SiteFooter />
    </>
  );
}
