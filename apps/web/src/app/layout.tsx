import type { Metadata, Viewport } from "next";
import { inter, instrumentSans, instrumentSerif } from "@/app/fonts";
import { SkipLink } from "@/components/layout/skip-link";
import { SmoothScrollProvider } from "@/components/providers/smooth-scroll-provider";
import { company } from "@/lib/content/company";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://thehivelogistics.fr";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "THE HIVE LOGISTICS — Convoyage automobile",
    template: "%s — THE HIVE LOGISTICS",
  },
  description:
    "THE HIVE LOGISTICS — convoyage automobile, gestion de flotte et logistique automobile.",
  openGraph: {
    title: "THE HIVE LOGISTICS — Convoyage automobile",
    description: "Convoyage automobile, gestion de flotte et logistique automobile.",
    type: "website",
    locale: "fr_FR",
    siteName: "THE HIVE LOGISTICS",
    images: [{ url: "/opengraph-image", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "THE HIVE LOGISTICS — Convoyage automobile",
    description: "Convoyage automobile, gestion de flotte et logistique automobile.",
    images: ["/opengraph-image"],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "THE HIVE LOGISTICS",
    description: "THE HIVE LOGISTICS — convoyage automobile, gestion de flotte et logistique automobile.",
    url: siteUrl,
    /*
     * TODO V3.1: remplacer par le logo officiel THE HIVE (abeille) quand Jores fournira les
     * sources SVG/PNG haute résolution. Trois consommateurs à mettre à jour ensemble :
     * app/icon.svg (favicon 32×32), app/apple-icon.svg (180×180) et le mot-symbole texte du
     * header (components/layout/site-header.tsx), aujourd'hui un monogramme « H » provisoire.
     */
    logo: `${siteUrl}/icon.svg`,
    email: company.email,
    telephone: company.phone.e164,
    vatID: company.vatId,
    address: {
      "@type": "PostalAddress",
      streetAddress: company.address.street,
      postalCode: company.address.postalCode,
      addressLocality: company.address.city,
      addressCountry: company.address.countryCode,
    },
  };

  return (
    <html
      lang="fr"
      className={`h-full ${instrumentSans.variable} ${instrumentSerif.variable} ${inter.variable}`}
    >
      <body className="min-h-full flex flex-col">
        <SkipLink />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
        <SmoothScrollProvider>{children}</SmoothScrollProvider>
      </body>
    </html>
  );
}
