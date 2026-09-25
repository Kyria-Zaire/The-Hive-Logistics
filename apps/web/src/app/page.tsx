import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { HeroSection } from "@/components/home/hero-section";
import { BrandStatementSection } from "@/components/home/brand-statement-section";
import { KeyFiguresSection } from "@/components/home/key-figures-section";
import { ServicesSection } from "@/components/home/services-section";
import { EngagementsSection } from "@/components/home/engagements-section";
import { MethodChapterSection } from "@/components/home/method-chapter-section";
import { VisionSection } from "@/components/home/vision-section";
import { ConversionSection } from "@/components/home/conversion-section";
import { TrustBannerSection } from "@/components/home/trust-banner-section";
export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="flex flex-1 flex-col">
        <HeroSection />
        <BrandStatementSection />
        <KeyFiguresSection />
        <ServicesSection />
        <EngagementsSection />
        <MethodChapterSection />
        <VisionSection showFolders />
        <ConversionSection />
        <TrustBannerSection />
      </main>
      <SiteFooter />
    </>
  );
}
