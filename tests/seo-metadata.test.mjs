import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { seoMetadata } from "../content/seo.ts";

test("RunRate metadata fallback keeps page copy and sets the canonical route", () => {
  const metadata = seoMetadata("/diagnostic", {
    title: "Business Independence Diagnostic",
    description: "Existing description",
  });
  assert.equal(metadata.title, "Business Independence Diagnostic");
  assert.equal(metadata.description, "Existing description");
  assert.equal(metadata.alternates.canonical, "https://www.runrategroup.com/diagnostic");
});

test("SEO overrides start empty and cannot silently retag the website", async () => {
  const overrides = JSON.parse(await readFile(new URL("../content/seo-overrides.json", import.meta.url)));
  assert.deepEqual(overrides, {});
});
