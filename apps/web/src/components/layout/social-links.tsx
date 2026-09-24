import { company } from "@/lib/content/company";

/**
 * Liens vers les comptes officiels, partagés par le pied de page et /contact.
 *
 * Les glyphes sont dessinés ici plutôt qu'importés : lucide-react 1.45 ne fournit plus aucune
 * icône de marque, et les deux signes sont des marques déposées. On en garde une rendition
 * géométrique au trait, monochrome et héritée de la couleur du texte — usage nominatif, sans
 * recoloration ni déformation, et sans dépendance supplémentaire.
 */

const glyphAttributes = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.75,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
  focusable: false,
} as const;

function InstagramGlyph() {
  return (
    <svg {...glyphAttributes}>
      <rect x="2.75" y="2.75" width="18.5" height="18.5" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.5" r="1.05" fill="currentColor" stroke="none" />
    </svg>
  );
}

function LinkedInGlyph() {
  return (
    <svg {...glyphAttributes}>
      <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z" />
      <rect x="2" y="9" width="4" height="12" />
      <circle cx="4" cy="4" r="2" />
    </svg>
  );
}

const networks = [
  { key: "instagram", Glyph: InstagramGlyph, ...company.social.instagram },
  { key: "linkedin", Glyph: LinkedInGlyph, ...company.social.linkedin },
] as const;

type SocialLinksProps = {
  /** Classes de la liste. */
  className?: string;
  /** Classes du lien, pour accorder la couleur au fond (sombre en pied de page, clair sur /contact). */
  linkClassName?: string;
};

export function SocialLinks({ className = "", linkClassName = "" }: SocialLinksProps) {
  const published = networks.filter((network) => network.url.length > 0);

  if (published.length === 0) {
    return null;
  }

  return (
    <ul className={`flex flex-col gap-[var(--space-3)] ${className}`}>
      {published.map(({ key, Glyph, label, url, handle }) => (
        <li key={key}>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            // Le nom accessible reprend le texte visible (WCAG 2.5.3, commande vocale) et
            // annonce l'ouverture dans un nouvel onglet, que rien d'autre ne signale.
            aria-label={`${label} — ${handle} (nouvelle fenêtre)`}
            className={`inline-flex items-center gap-[var(--space-2)] ${linkClassName}`}
          >
            <Glyph />
            <span>{handle}</span>
          </a>
        </li>
      ))}
    </ul>
  );
}
