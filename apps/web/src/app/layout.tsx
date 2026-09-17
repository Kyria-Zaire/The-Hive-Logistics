import type { Metadata, Viewport } from "next";
import { instrumentSans, instrumentSerif } from "@/app/fonts";
import { SkipLink } from "@/components/layout/skip-link";
import { company } from "@/lib/content/company";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://thehivelogistics.fr";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "THE HIVE LOGISTICS — Convoyage automobile premium",
    template: "%s — THE HIVE LOGISTICS",
  },
  description:
    "THE HIVE LOGISTICS — convoyage automobile premium, gestion de flotte et logistique haut de gamme.",
  openGraph: {
    title: "THE HIVE LOGISTICS — Convoyage automobile premium",
    description: "Convoyage automobile, gestion de flotte, logistique premium et préparation automobile.",
    type: "website",
    locale: "fr_FR",
    siteName: "THE HIVE LOGISTICS",
    images: [{ url: "/opengraph-image", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "THE HIVE LOGISTICS — Convoyage automobile premium",
    description: "Convoyage automobile, gestion de flotte, logistique premium et préparation automobile.",
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
    description: "THE HIVE LOGISTICS — convoyage automobile premium, gestion de flotte et logistique haut de gamme.",
    url: siteUrl,
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
      className={`h-full ${instrumentSans.variable} ${instrumentSerif.variable}`}
    >
      <body className="min-h-full flex flex-col">
        <SkipLink />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
        {children}
      </body>
    </html>
  );
}
