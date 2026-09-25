"use client";

import { useEffect, useState } from "react";
import { Car, Target, TrendingUp, Zap, type LucideIcon } from "lucide-react";
import { homeContent } from "@/lib/content/home";

/**
 * TICKET 34 — les quatre volets de la vision, en dossiers qu'on ouvre.
 *
 * Un seul ouvert à la fois : deux fiches dépliées côte à côte se marcheraient dessus, la
 * feuille sortant du flux.
 */

const ICONS: Record<string, LucideIcon> = {
  target: Target,
  "trending-up": TrendingUp,
  car: Car,
  zap: Zap,
};

type FolderProps = {
  /** Sert d'intitulé au bouton et de titre à la fiche. */
  label: string;
  description: string;
  Icon: LucideIcon;
  isOpen: boolean;
  onToggle: () => void;
  /**
   * Identifiants dérivés de l'index, pas du libellé : « MOBILITÉ INTÉGRÉE » contient une
   * espace, et un `id` avec une espace est invalide — `aria-controls` y lirait deux
   * identifiants au lieu d'un.
   */
  paperId: string;
  titleId: string;
};

function Folder({ label, description, Icon, isOpen, onToggle, paperId, titleId }: FolderProps) {
  return (
    <div className={`thl-folder ${isOpen ? "thl-folder--open" : ""}`}>
      {/* Un vrai bouton : focus, Entrée et Espace viennent du navigateur, et le titre de la
          fiche reste un h3 — un h3 dans un bouton serait du contenu interactif imbriqué. */}
      <button
        type="button"
        className="thl-folder__button"
        onClick={onToggle}
        aria-expanded={isOpen}
        aria-controls={paperId}
      >
        <span className="thl-folder__back" aria-hidden="true">
          <span className="thl-folder__front" />
          <span className="thl-folder__front thl-folder__front--right" />
        </span>
        <span className="thl-folder__label">{label}</span>
      </button>

      <div
        id={paperId}
        className="thl-folder__paper"
        role="region"
        aria-labelledby={titleId}
        aria-hidden={!isOpen}
      >
        <span className="thl-folder__icon" aria-hidden="true">
          <Icon size={20} strokeWidth={1.75} />
        </span>
        <h3 id={titleId} className="thl-folder__title">
          {label}
        </h3>
        <p className="thl-folder__description">{description}</p>
      </div>
    </div>
  );
}

export function VisionFolders() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const { vision } = homeContent;

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpenIndex(null);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div
      className={`thl-vision-folders ${
        openIndex !== null ? "thl-vision-folders--has-open" : ""
      }`}
    >
      <ul className="thl-vision-folders__grid">
        {vision.folders.map((folder, index) => (
          <li
            key={folder.label}
            className={`thl-vision-folders__item ${
              openIndex === index ? "thl-vision-folders__item--open" : ""
            }`}
          >
            <Folder
              label={folder.label}
              description={folder.description}
              Icon={ICONS[folder.icon] ?? Target}
              isOpen={openIndex === index}
              onToggle={() => setOpenIndex(openIndex === index ? null : index)}
              paperId={`vision-folder-paper-${index}`}
              titleId={`vision-folder-title-${index}`}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}
