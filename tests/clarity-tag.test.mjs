import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const component = readFileSync("components/MicrosoftClarity.tsx", "utf8");
const layout = readFileSync("app/layout.tsx", "utf8");

test("Microsoft Clarity loads the configured project tag from the shared layout", () => {
  assert.match(component, /clarity\.ms\/tag\//);
  assert.match(component, /NEXT_PUBLIC_CLARITY_PROJECT_ID/);
  assert.match(component, /strategy=\"afterInteractive\"/);
  assert.match(component, /clarity/);
  assert.match(layout, /<MicrosoftClarity\s*\/>/);
});
