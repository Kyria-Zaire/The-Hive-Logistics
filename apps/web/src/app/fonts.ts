import { Inter, Instrument_Sans, Instrument_Serif } from "next/font/google";

/**
 * Display family, chargée aux deux seuls poids que `--font-display` réclame réellement
 * (TICKET 33) : 600 pour les quatre classes `.text-display-*` passées en capitales grasses,
 * 300 pour le lede du hero et les chiffres clés, qui restent en Light.
 *
 * Pas de 400 : aucune règle ne l'utilise. Le retirer du 300 aurait fait retomber le lede et
 * les chiffres sur la graisse la plus proche disponible — les navigateurs ne synthétisent
 * pas un poids plus léger que ce qu'on leur donne.
 */
export const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["300", "600"],
});

export const instrumentSans = Instrument_Sans({
  subsets: ["latin", "latin-ext"],
  variable: "--font-instrument-sans",
  display: "swap",
  weight: ["400", "500", "600"],
});

export const instrumentSerif = Instrument_Serif({
  subsets: ["latin", "latin-ext"],
  variable: "--font-instrument-serif",
  display: "swap",
  weight: ["400"],
  style: ["italic"],
});
