import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const configPath = "infra/cloudflare/runrate-edge-security.rulesets.json";
const managedRuleRefs = new Set([
  "rr_strict_sensitive_api_ip_5_per_min",
  "rr_sensitive_api_burst_5_per_10_seconds",
  "rr_moderate_public_api_ip_10_per_min",
  "rr_future_auth_strict_5_per_min_disabled_until_routes_exist",
  "rr_future_registration_moderate_10_per_min_disabled_until_routes_exist",
  "rr_challenge_admin_missing_access_email_defense_in_depth",
  "rr_log_sqli_signals",
  "rr_log_xss_signals",
  "rr_log_lfi_path_traversal_signals",
  "rr_bot_challenge_sensitive_routes_score_lt_30_disabled_until_plan_confirmed",
]);

export function validateCloudflareZoneId(value) {
  if (/^[a-f0-9]{32}$/i.test(value)) return true;
  throw new Error(
    "CLOUDFLARE_ZONE_ID must be the 32-character zone ID for runrategroup.com, not an API token. Find it in Cloudflare → Websites → runrategroup.com → Overview → API → Zone ID.",
  );
}

function requireEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is required`);
  return value;
}

async function cfFetch(path, init = {}) {
  const token = requireEnv("CLOUDFLARE_API_TOKEN");
  const response = await fetch(`https://api.cloudflare.com/client/v4${path}`, {
    ...init,
    headers: {
      authorization: `Bearer ${token}`,
      "content-type": "application/json",
      ...(init.headers ?? {}),
    },
  });
  const body = await response.json();
  if (!response.ok || body.success === false) {
    throw new Error(JSON.stringify(body, null, 2));
  }
  return body.result;
}

async function getEntryPoint(zoneId, phase) {
  try {
    return await cfFetch(`/zones/${zoneId}/rulesets/phases/${phase}/entrypoint`);
  } catch (error) {
    const message = String(error.message);
    if (message.includes("could not find") || message.includes("not found")) return null;
    throw error;
  }
}

function loadConfig() {
  return JSON.parse(readFileSync(configPath, "utf8"));
}

export function getDeployableRulesets(config) {
  return {
    ...config,
    rulesets: Object.fromEntries(
      Object.entries(config.rulesets).map(([key, ruleset]) => [
        key,
        {
          ...ruleset,
          rules: ruleset.rules.filter((rule) => rule.enabled !== false),
        },
      ]),
    ),
  };
}

function mergeRules(existingRules = [], managedRules = []) {
  const unmanagedRules = existingRules.filter((rule) => !managedRuleRefs.has(rule.ref));
  return [...unmanagedRules, ...managedRules];
}

function toRulesetPayload(ruleset, existing = null) {
  return {
    ...(existing ?? {}),
    name: ruleset.name,
    description: ruleset.description,
    kind: ruleset.kind,
    phase: ruleset.phase,
    rules: mergeRules(existing?.rules, ruleset.rules),
  };
}

async function upsertRuleset(zoneId, ruleset) {
  const existing = await getEntryPoint(zoneId, ruleset.phase);
  const payload = toRulesetPayload(ruleset, existing);
  if (!existing) {
    return cfFetch(`/zones/${zoneId}/rulesets`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }
  return cfFetch(`/zones/${zoneId}/rulesets/${existing.id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

function plan(config) {
  const phases = Object.values(config.rulesets).map((ruleset) => ({
    phase: ruleset.phase,
    name: ruleset.name,
    rules: ruleset.rules.map((rule) => ({
      ref: rule.ref,
      action: rule.action,
      enabled: rule.enabled ?? true,
    })),
  }));
  console.log(JSON.stringify({ zone: config.zone, hostnames: config.hostnames, phases }, null, 2));
}

async function deploy(config) {
  const zoneId = requireEnv("CLOUDFLARE_ZONE_ID");
  validateCloudflareZoneId(zoneId);
  const customWaf = await upsertRuleset(zoneId, config.rulesets.http_request_firewall_custom);
  const rateLimit = await upsertRuleset(zoneId, config.rulesets.http_ratelimit);
  console.log(JSON.stringify({
    status: "deployed",
    customWaf: { id: customWaf.id, phase: customWaf.phase, version: customWaf.version },
    rateLimit: { id: rateLimit.id, phase: rateLimit.phase, version: rateLimit.version },
  }, null, 2));
}

async function main() {
  const command = process.argv[2] ?? "plan";
  const config = loadConfig();

  if (command === "plan") {
    plan(getDeployableRulesets(config));
    return;
  }

  if (command === "deploy") {
    await deploy(getDeployableRulesets(config));
    return;
  }

  throw new Error(`Unknown command: ${command}`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
