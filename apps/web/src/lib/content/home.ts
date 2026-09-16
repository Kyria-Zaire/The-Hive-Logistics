export const homeContent = {
  hero: {
    ctaPrimary: "Réserver un convoyage",
    ctaSecondary: "Découvrir nos services",
  },
  brandStatement: {
    title: "Une logistique automobile pensée avec rigueur",
    body:
      "Chaque déplacement exige anticipation, clarté et respect du véhicule. Nous structurons la demande, qualifions le besoin avec vous et organisons la prise en charge sans promesse automatisée.",
    linkLabel: "Découvrir notre approche",
  },
  services: {
    eyebrow: "NOS SERVICES",
    title: "Une offre complète",
    items: [
      {
        id: "convoyage",
        title: "Convoyage automobile",
        description: "Déplacement sécurisé de votre véhicule.",
        icon: "route",
      },
      {
        id: "flotte",
        title: "Gestion de flotte",
        description: "Coordination et suivi de votre flotte.",
        icon: "fleet",
      },
      {
        id: "logistique",
        title: "Logistique premium",
        description: "Solutions logistiques adaptées à votre besoin.",
        icon: "package",
      },
      {
        id: "preparation",
        title: "Préparation automobile",
        description: "Préparation soignée avant remise des clés.",
        icon: "sparkle",
      },
    ],
  },
  engagements: {
    eyebrow: "NOTRE ENGAGEMENT",
    title: "Le luxe, une exigence",
    items: [
      {
        title: "Excellence opérationnelle",
        description:
          "Rigueur et méthode à chaque étape.",
      },
      {
        title: "Disponibilité renforcée",
        description:
          "Une équipe disponible aux horaires convenus.",
      },
      {
        title: "Confidentialité renforcée",
        description:
          "Vos véhicules et vos données sont protégés.",
      },
    ],
  },
  methodChapter: {
    eyebrow: "NOTRE MÉTHODE",
    chapterTitle: "Un processus maîtrisé",
    note:
      "Chaque demande est traitée par l'équipe — pas de confirmation automatique en ligne.",
    steps: [
      {
        num: "01",
        title: "Réservation",
        text: "Soumettez votre demande via le formulaire.",
      },
      {
        num: "02",
        title: "Prise en charge",
        text: "Nous confirmons les modalités avec vous.",
      },
      {
        num: "03",
        title: "Transport sécurisé",
        text: "Votre véhicule est acheminé avec soin.",
      },
      {
        num: "04",
        title: "Livraison",
        text: "Remise du véhicule au lieu convenu.",
      },
    ],
    principlesTitle: "Nos principes",
    principles: [
      {
        num: "01",
        title: "Communication claire",
        text: "Points de contact et étapes expliqués.",
      },
      {
        num: "02",
        title: "Prise en charge structurée",
        text: "Processus défini pour chaque demande.",
      },
      {
        num: "03",
        title: "Respect du véhicule",
        text: "Exigence centrale de notre métier.",
      },
      {
        num: "04",
        title: "Suivi humain",
        text: "Un interlocuteur dédié, défini avec vous.",
      },
    ],
    cta: "Demander un devis",
  },
  vision: {
    eyebrow: "NOTRE VISION",
    title: "Bâtir la référence du convoyage premium en France.",
    body:
      "Faire de chaque déplacement une référence. Nous construisons une mobilité premium fondée sur la précision, la rigueur et la confiance. Notre ambition est de développer une présence nationale du convoyage haut de gamme, en accompagnant chaque véhicule avec le même niveau d’exigence. Le prestige ne tient pas à l’apparence seule : il se mesure à la qualité constante de chaque étape, à la clarté des échanges et au respect des engagements pris.",
  },
  conversion: {
    title: "Parlons de votre besoin",
    body: "Décrivez votre demande de devis ou contactez-nous.",
    ctaPrimary: "Demander un devis",
    ctaSecondary: "Nous contacter",
  },
  footer: {
    wordmark: "THE HIVE LOGISTICS",
    nav: {
      services: "Services",
      about: "À propos",
      contact: "Contact",
      quote: "Devis",
    },
    legal: {
      mentions: "Mentions légales",
      privacy: "Politique de confidentialité",
    },
  },
  nav: {
    home: "Accueil",
    services: "Services",
    contact: "Contact",
    quote: "Demander un devis",
    menuOpen: "Ouvrir le menu",
    menuClose: "Fermer le menu",
    primary: "Navigation principale",
  },
} as const;

/** Textes interdits en surface publique (tests de non-régression). */
export const forbiddenPublicPhrases = [
  "immobilier",
  "chauffeur privé",
  "chauffeur prive",
] as const;
