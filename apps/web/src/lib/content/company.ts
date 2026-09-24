/** Données légales et coordonnées de l'éditeur, transmises par Jores (TICKET 10-UNDECIES). */
export const company = {
  legalName: "The HIVE LOGISTICS",
  legalForm: "SASU (SAS à associé unique)",
  shareCapital: "100 €",
  president: "Jores DZOUALOU NDZABA",
  address: {
    street: "78 Rue Frédéric Passy",
    postalCode: "51430",
    city: "Bezannes",
    countryCode: "FR",
  },
  registration: "105 735 864 R.C.S. Reims",
  vatId: "FR47105735864",
  email: "contact@thehivelogistics.fr",
  phone: {
    display: "06 21 23 96 43",
    e164: "+33621239643",
  },
  host: "Vercel Inc., 440 N Barranca Ave #4133, Covina, CA 91723, États-Unis",
  dataRetention: "3 ans à compter du dernier contact",
  /**
   * Réseaux sociaux officiels. Un réseau dont l'`url` est vide n'est pas rendu : mieux vaut
   * pas de lien qu'un lien mort. LinkedIn attend l'URL de Jores (TICKET 30).
   */
  social: {
    instagram: {
      label: "Instagram",
      url: "https://www.instagram.com/the.hive.logistics",
      handle: "@the.hive.logistics",
    },
    linkedin: {
      label: "LinkedIn",
      url: "",
      handle: "",
    },
  },
} as const;

export const companyAddressLine = `${company.address.street}, ${company.address.postalCode} ${company.address.city}`;
