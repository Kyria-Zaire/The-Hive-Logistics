export const homeContent = {
  hero: {
    eyebrow: "Mobilité automobile premium",
    h1Before: "Nous déplaçons ",
    h1Accent: "plus que",
    h1After: " des véhicules.",
    paragraph:
      "Convoyage, gestion de flotte et logistique automobile, orchestrés avec précision.",
    ctaPrimary: "Demander un devis",
    ctaSecondary: "Découvrir nos services",
  },
  brandStatement: {
    title: "Une logistique automobile pensée avec rigueur",
    body:
      "Chaque déplacement exige anticipation, clarté et respect du véhicule. Nous structurons la demande, qualifions le besoin avec vous et organisons la prise en charge sans promesse automatisée.",
    linkLabel: "Découvrir notre approche",
  },
  services: {
    title: "Nos expertises",
    cta: "Voir tous les services",
    items: [
      {
        id: "convoyage",
        title: "Convoyage automobile premium",
        need: "Organiser le déplacement de véhicules",
        description:
          "Accompagnement du déplacement de véhicules selon votre contexte.",
      },
      {
        id: "flotte",
        title: "Gestion et coordination de flotte",
        need: "Coordonner les mouvements",
        description:
          "Coordination opérationnelle des mouvements de flotte.",
      },
      {
        id: "logistique",
        title: "Logistique automobile",
        need: "Structurer les flux",
        description:
          "Accompagnement logistique automobile adapté à vos contraintes.",
      },
      {
        id: "preparation",
        title: "Préparation automobile",
        need: "Préparer la remise",
        description:
          "Préparation automobile selon le périmètre validé.",
      },
    ],
  },
  methodChapter: {
    chapterTitle: "La méthode Hive",
    processTitle: "Comment se déroule une demande",
    note:
      "Chaque demande est traitée par l'équipe — pas de confirmation automatique en ligne.",
    steps: [
      {
        num: "01",
        title: "Demande",
        text: "Vous formulez votre besoin via le devis ou le contact.",
      },
      {
        num: "02",
        title: "Qualification",
        text: "Nous examinons les informations et reprenons contact si nécessaire.",
      },
      {
        num: "03",
        title: "Prise en charge",
        text: "Organisation opérationnelle du service convenu.",
      },
      {
        num: "04",
        title: "Livraison et confirmation",
        text: "Restitution et confirmation avec vous.",
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
        text: "Modalités d'interlocuteur définies avec vous.",
      },
    ],
    cta: "Demander un devis",
  },
  vision: {
    title: "Perspectives",
    body:
      "THE HIVE LOGISTICS oriente son développement vers des services de mobilité automobile premium — coordination, logistique et préparation — avec une ambition d'élargissement progressif des services proposés, sous validation métier et juridique.",
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
      cookies: "Politique cookies",
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
] as const;
