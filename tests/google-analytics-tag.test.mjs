import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const component = readFileSync("components/GoogleAnalytics.tsx", "utf8");
const layout = readFileSync("app/layout.tsx", "utf8");

test("Google Analytics loads the configured gtag script from the shared layout", () => {
  assert.match(component, /googletagmanager\.com\/gtag\/js\?id=/);
  assert.match(component, /NEXT_PUBLIC_GA_MEASUREMENT_ID/);
  assert.match(component, /strategy=\"afterInteractive\"/);
  assert.match(component, /gtag\('config'/);
  assert.match(layout, /<GoogleAnalytics\s*\/>/);
});

test("Google Analytics does not fall back to a previous site ID", () => {
  assert.match(component, /if\s*\(!measurementId\)\s*return\s+null/);
  assert.doesNotMatch(component, /G-VPP81LYJ0Y/);
});
