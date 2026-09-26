import { homeContent } from "@/lib/content/home";
import { VisionFolders } from "@/components/home/vision-folders";

type VisionSectionProps = {
  /**
   * Les quatre dossiers. Optionnel : la section reste utilisable en énoncé seul si une page
   * n'en veut pas.
   */
  showFolders?: boolean;
};

/**
 * TICKET 34 — l'énoncé de vision, suivi de quatre dossiers qu'on ouvre.
 *
 * Fond noir uni : la photographie et ses deux voiles ont été retirés sur décision client, la
 * section Engagements juste au-dessus portant déjà l'image.
 *
 * Les libellés, titres et descriptions des dossiers sont rendus ici, côté serveur : ils sont
 * dans le HTML avant le moindre script. Seule l'ouverture est cliente.
 */
export function VisionSection({ showFolders = false }: VisionSectionProps) {
  const { vision } = homeContent;

  return (
    <section
      aria-labelledby="vision-heading"
      className="section-dark bg-[var(--bg-primary)] py-[var(--space-7)]"
    >
      <div className="thl-container">
        <div className="mx-auto max-w-4xl text-center">
          <h2 id="vision-heading" className="text-display-m text-[var(--text-primary)]">
            {vision.eyebrow}
          </h2>
          {/* En `.text-heading` (32 px) et non `.text-section-subtitle` (26 px) : c'est la
              phrase la plus forte du site, elle garde du poids sous son libellé. */}
          <p className="text-heading mt-4 text-[var(--text-secondary)]">{vision.title}</p>
          <p className="text-body-l mt-[var(--space-4)] text-[var(--text-secondary)]">
            {vision.intro}
          </p>
        </div>

        {showFolders ? <VisionFolders /> : null}
      </div>
    </section>
  );
}
