import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import {
  getDeployableRulesets,
  validateCloudflareZoneId,
} from "../scripts/cloudflare-edge-security.mjs";

const config = JSON.parse(readFileSync("infra/cloudflare/runrate-edge-security.rulesets.json", "utf8"));

test("rate limit configuration preserves edge and upgrade-template route policies", () => {
  const rules = config.rulesets.http_ratelimit.rules;
  assert.ok(rules.some((rule) => rule.ref === "rr_sensitive_api_burst_5_per_10_seconds"));
  assert.ok(rules.some((rule) => rule.ref === "rr_moderate_public_api_ip_10_per_min"));
  assert.match(JSON.stringify(rules), /api\/assessment\/calculate/);
  assert.match(JSON.stringify(rules), /api\/contact/);
  assert.match(JSON.stringify(rules), /api\/analytics\/events/);
});

test("deployable rate limits fit the zone plan's one-rule entitlement", () => {
  const deployable = getDeployableRulesets(config);
  assert.equal(deployable.rulesets.http_ratelimit.rules.length, 1);
  assert.equal(
    deployable.rulesets.http_ratelimit.rules[0].ref,
    "rr_sensitive_api_burst_5_per_10_seconds",
  );
});

test("deployable rate limit uses Free-plan period, timeout, and fields", () => {
  const deployable = getDeployableRulesets(config);
  const [rule] = deployable.rulesets.http_ratelimit.rules;
  assert.equal(rule.ratelimit.period, 10);
  assert.equal(rule.ratelimit.mitigation_timeout, 10);
  assert.equal(rule.ratelimit.requests_per_period, 5);
  assert.doesNotMatch(rule.expression, /http\.host/);
  assert.doesNotMatch(rule.expression, /\/admin\//);
  assert.doesNotMatch(rule.expression, /\/api\/analytics\/(snapshot|stream)/);
});

test("broad WAF rules use managed challenge when log action is unavailable", () => {
  const rules = config.rulesets.http_request_firewall_custom.rules;
  for (const ref of ["rr_log_sqli_signals", "rr_log_xss_signals", "rr_log_lfi_path_traversal_signals"]) {
    const rule = rules.find((candidate) => candidate.ref === ref);
    assert.equal(rule?.action, "managed_challenge");
  }
});

test("bot score rule is disabled by default because plan support is not guaranteed", () => {
  const botRules = config.rulesets.http_request_firewall_custom.rules.filter((rule) =>
    rule.expression.includes("cf.bot_management.score"),
  );
  assert.ok(botRules.length >= 1);
  assert.ok(botRules.every((rule) => rule.enabled === false));
});

test("deployable rulesets omit disabled rules with unavailable enterprise-only fields", () => {
  const deployable = getDeployableRulesets(config);
  const raw = JSON.stringify(deployable);
  assert.doesNotMatch(raw, /cf\.bot_management\.score/);
});

test("deployable rulesets do not use the unavailable log action", () => {
  const deployable = getDeployableRulesets(config);
  const actions = Object.values(deployable.rulesets).flatMap((ruleset) =>
    ruleset.rules.map((rule) => rule.action),
  );
  assert.ok(!actions.includes("log"));
});

test("deployable rulesets do not use the unavailable regex matches operator", () => {
  const deployable = getDeployableRulesets(config);
  const expressions = Object.values(deployable.rulesets).flatMap((ruleset) =>
    ruleset.rules.map((rule) => rule.expression),
  );
  assert.ok(expressions.every((expression) => !expression.includes(" matches ")));
});

test("static asset bypasses are present in broad WAF expressions", () => {
  const rules = config.rulesets.http_request_firewall_custom.rules.filter((rule) =>
    rule.ref.startsWith("rr_log_"),
  );
  for (const rule of rules) {
    assert.match(rule.expression, /\/_next\//);
    assert.match(rule.expression, /\.css/);
    assert.match(rule.expression, /\.mp4/);
  }
});

test("WAF expressions detect encoded SQLi and XSS query payloads", () => {
  const rules = config.rulesets.http_request_firewall_custom.rules;
  const sqli = rules.find((rule) => rule.ref === "rr_log_sqli_signals");
  const xss = rules.find((rule) => rule.ref === "rr_log_xss_signals");
  assert.match(sqli.expression, /union%20select/);
  assert.match(xss.expression, /%3cscript/);
});

test("verification script reports probe status codes without dumping response bodies", () => {
  const script = readFileSync("scripts/verify-cloudflare-edge-security.ps1", "utf8");
  assert.match(script, /SQLi status %\{http_code\}/);
  assert.match(script, /XSS status %\{http_code\}/);
  assert.doesNotMatch(script, /curl\.exe -i/);
});

test("future auth route templates remain disabled until those app routes exist", () => {
  const rules = config.rulesets.http_ratelimit.rules.filter((rule) => rule.ref.startsWith("rr_future_"));
  assert.equal(rules.length, 2);
  assert.ok(rules.every((rule) => rule.enabled === false));
});

test("deployment guard accepts only Cloudflare zone-id shaped values", () => {
  assert.equal(validateCloudflareZoneId("023e105f4ecef8ad9ca31a8372d0c353"), true);
});

test("deployment guard rejects token-shaped values accidentally pasted as the zone id", () => {
  assert.throws(
    () => validateCloudflareZoneId(`cfut_${"x".repeat(64)}`),
    /CLOUDFLARE_ZONE_ID must be the 32-character zone ID/,
  );
});
