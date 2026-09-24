import { Inter, Instrument_Sans, Instrument_Serif } from "next/font/google";

/** Display family: Instrument Sans has no weight below 400. */
export const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["300", "400"],
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
