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
  /** Chiffres fournis et validés par Jores (aucune valeur estimée). */
  keyFigures: {
    label: "Chiffres clés",
    // Number and suffix apart, rather than "300+" as one string: the count-up animates the
    // number and must never touch the sign, and a number is also what it needs to count to.
    items: [
      { value: 300, suffix: "+", label: "VÉHICULES CONVOYÉS / AN" },
      { value: 25000, suffix: "+", label: "KILOMÈTRES PARCOURUS / AN" },
      { value: 95, suffix: "%", label: "MISSIONS DANS LES DÉLAIS" },
    ],
  },
  services: {
    eyebrow: "NOS SERVICES",
    title: "Une offre complète",
    items: [
      {
        id: "convoyage",
        title: "Convoyage automobile",
        description: "Déplacement sécurisé de votre véhicule.",
        image: "/images/services/convoyage.jpg",
      },
      {
        id: "flotte",
        title: "Gestion de flotte",
        description: "Coordination et suivi de votre flotte.",
        image: "/images/services/flotte.jpg",
      },
      {
        id: "logistique",
        title: "Logistique automobile",
        description: "Solutions logistiques adaptées à votre besoin.",
        image: "/images/services/logistique.jpg",
      },
    ],
  },
  engagements: {
    eyebrow: "NOTRE ENGAGEMENT",
    title: "La logistique, une exigence",
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
    title: "Bâtir la référence du convoyage automobile en France.",
    body:
      "Faire de chaque déplacement une référence. Nous construisons une mobilité fondée sur la précision, la rigueur et la confiance. Notre ambition est de développer une présence nationale du convoyage automobile, en accompagnant chaque véhicule avec le même niveau d’exigence. Le prestige ne tient pas à l’apparence seule : il se mesure à la qualité constante de chaque étape, à la clarté des échanges et au respect des engagements pris.",
  },
  /**
   * Bannière partenaires — structure seule.
   * Les noms ne sont PAS rendus tant que `src` est null : afficher une marque
   * tierce sans autorisation engagerait THE HIVE LOGISTICS.
   * Activation : renseigner `src` avec le chemin dans /public/images/partners/
   * puis passer SHOW_TRUST_BANNER à true. Droits à confirmer par Jores.
   */
  trustBanner: {
    title: "Ils nous font confiance",
    logos: [
      { name: "DLM", src: null },
      { name: "Sixt", src: null },
      { name: "Europcar", src: null },
      { name: "Audi", src: null },
      { name: "Mercedes", src: null },
      { name: "BMW", src: null },
      { name: "Peugeot", src: null },
      { name: "Renault", src: null },
      { name: "Mosolf", src: null },
    ],
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
    about: "À propos",
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
  "préparation automobile",
  "preparation automobile",
] as const;
