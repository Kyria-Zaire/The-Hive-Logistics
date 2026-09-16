import type { MetadataRoute } from "next";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://the-hive-logistics.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date();
  return [
    { url: siteUrl, lastModified, changeFrequency: "monthly", priority: 1 },
    { url: `${siteUrl}/contact`, lastModified, changeFrequency: "monthly", priority: 0.9 },
    { url: `${siteUrl}/services`, lastModified, changeFrequency: "monthly", priority: 0.9 },
    { url: `${siteUrl}/a-propos`, lastModified, changeFrequency: "monthly", priority: 0.7 },
    { url: `${siteUrl}/mentions-legales`, lastModified, changeFrequency: "yearly", priority: 0.3 },
    { url: `${siteUrl}/politique-de-confidentialite`, lastModified, changeFrequency: "yearly", priority: 0.3 },
  ];
}