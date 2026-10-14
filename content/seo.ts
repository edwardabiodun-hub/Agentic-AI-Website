import type { Metadata } from "next";
import overrides from "./seo-overrides.json";

type SeoOverride = { title: string; description: string };
const entries = overrides as Record<string, SeoOverride>;

export function seoMetadata(route: string, fallback: Metadata): Metadata {
  const override = entries[route];
  const base = (process.env.NEXT_PUBLIC_SITE_URL || "https://www.runrategroup.com").replace(/\/$/, "");
  return {
    ...fallback,
    ...(override ? { title: { absolute: override.title }, description: override.description } : {}),
    alternates: { ...fallback.alternates, canonical: `${base}${route === "/" ? "" : route}` },
  };
}
