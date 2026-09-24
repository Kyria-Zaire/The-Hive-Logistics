import Image from "next/image";
import { homeContent } from "@/lib/content/home";
import { SHOW_TRUST_BANNER } from "@/lib/features";

/**
 * Bannière partenaires — structure seule, pas encore publiable.
 *
 * Activation, quand Jores aura confirmé les droits (mail en attente) :
 *   1. déposer les fichiers dans /public/images/partners/ ;
 *   2. remplacer `src: null` par le chemin du logo dans `home.ts` ;
 *   3. passer SHOW_TRUST_BANNER à true dans lib/features.ts.
 *
 * Tant que `src` vaut null, le slot reste anonyme : aucun nom de marque n'est
 * rendu, afficher un partenaire non confirmé engagerait l'entreprise.
 */
export function TrustBannerSection() {
  const { trustBanner } = homeContent;

  if (!SHOW_TRUST_BANNER) {
    return null;
  }

  return (
    <section
      aria-labelledby="trust-banner-heading"
      className="section-light py-[var(--space-6)] lg:py-[var(--space-7)]"
    >
      <div className="thl-container">
        <h2
          id="trust-banner-heading"
          className="text-display-m text-center text-[var(--text-dark-primary)]"
        >
          {trustBanner.title}
        </h2>
        <ul className="mt-[var(--space-6)] grid grid-cols-2 gap-[var(--space-5)] md:grid-cols-4 lg:grid-cols-5">
          {trustBanner.logos.map((logo) => (
            <li key={logo.name} className="flex items-center justify-center">
              {logo.src === null ? (
                <div
                  className="flex aspect-3/2 w-full items-center justify-center border border-[var(--border-light)] bg-[var(--bg-light-elevated)]"
                  aria-hidden
                >
                  <span className="text-caption text-[var(--text-dark-muted)]">
                    Logo partenaire
                  </span>
                </div>
              ) : (
                <Image
                  src={logo.src}
                  alt={logo.name}
                  width={160}
                  height={40}
                  className="h-10 w-auto opacity-60 grayscale transition-opacity duration-[var(--duration-fast)] ease-[var(--ease-lux)] hover:opacity-100 motion-reduce:transition-none"
                />
              )}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
