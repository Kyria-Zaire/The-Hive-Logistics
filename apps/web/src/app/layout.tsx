import type { Metadata, Viewport } from "next";
import { instrumentSans, instrumentSerif } from "@/app/fonts";
import { SkipLink } from "@/components/layout/skip-link";
import "./globals.css";

export const metadata: Metadata = {
  title: "THE HIVE LOGISTICS — Mobilité automobile premium",
  description:
    "Convoyage, coordination de flotte, logistique et préparation automobile premium. Demandez un devis ou contactez l'équipe.",
  openGraph: {
    title: "THE HIVE LOGISTICS — Mobilité automobile premium",
    description:
      "Convoyage, coordination de flotte, logistique et préparation automobile premium.",
    type: "website",
    locale: "fr_FR",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="fr"
      className={`h-full ${instrumentSans.variable} ${instrumentSerif.variable}`}
    >
      <body className="min-h-full flex flex-col overflow-x-hidden">
        <SkipLink />
        {children}
      </body>
    </html>
  );
}
