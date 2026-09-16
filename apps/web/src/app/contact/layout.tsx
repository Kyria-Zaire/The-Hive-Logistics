import type { Metadata } from "next";
import { ROUTES } from "@/lib/routes";

export const metadata: Metadata = {
  title: "Contact",
  description:
    "Contactez THE HIVE LOGISTICS pour votre projet de convoyage automobile, de gestion de flotte ou de logistique premium. Réponse via notre formulaire.",
  alternates: { canonical: ROUTES.contact },
};

export default function ContactLayout({ children }: LayoutProps<"/contact">) {
  return children;
}
