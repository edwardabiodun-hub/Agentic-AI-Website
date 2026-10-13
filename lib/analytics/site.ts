export const SITE_ANALYTICS_EVENTS = [
  "page_view",
  "session_heartbeat",
  "download_click",
  "form_start",
  "form_field_focus",
  "form_abandon",
  "form_submit",
  "assessment_step_view",
  "assessment_step_complete",
  "api_error",
  "api_latency",
] as const;

export type SiteAnalyticsEventName = (typeof SITE_ANALYTICS_EVENTS)[number];

type StringMap = Record<string, unknown>;

export type SiteAnalyticsEvent = {
  eventId: string;
  eventName: SiteAnalyticsEventName;
  occurredAt: string;
  anonymousId: string;
  sessionId: string;
  page: { path: string; title?: string; referrer?: string };
  source: { utmSource?: string; utmMedium?: string; utmCampaign?: string; hostname?: string };
  properties: Record<string, string | number | boolean>;
  performance: { durationMs?: number; statusCode?: number };
  context: { viewport?: string; deviceType?: string; userAgentFamily?: string };
};

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SAFE_PROPERTY_KEYS = new Set([
  "formId", "fieldName", "step", "fileType", "route", "screen", "label", "cta",
  "component", "errorType", "method", "endpoint", "status",
]);
const PII_KEY_PATTERN = /^(?:email|phone|name|address|company|answers?|notes?|message|free.?text)$/i;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function isRecord(value: unknown): value is StringMap {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function addError(errors: Record<string, string>, key: string, message: string) {
  if (!errors[key]) errors[key] = message;
}

function optionalString(value: unknown, key: string, errors: Record<string, string>, max = 240) {
  if (value === undefined || value === null) return undefined;
  if (typeof value !== "string" || value.length > max) {
    addError(errors, key, "must be a bounded string");
    return undefined;
  }
  return value;
}

function validateProperties(value: unknown, errors: Record<string, string>) {
  if (!isRecord(value)) {
    addError(errors, "properties", "must be an object");
    return {};
  }
  const result: Record<string, string | number | boolean> = {};
  for (const [key, raw] of Object.entries(value)) {
    if (!SAFE_PROPERTY_KEYS.has(key)) {
      addError(errors, `properties.${key}`, "property is not allowlisted");
      continue;
    }
    if (PII_KEY_PATTERN.test(key) || (typeof raw === "string" && (EMAIL_PATTERN.test(raw) || /\+?\d[\d ()-]{7,}/.test(raw)))) {
      addError(errors, `properties.${key}`, "PII-like values are not accepted");
      continue;
    }
    if (!["string", "number", "boolean"].includes(typeof raw) || (typeof raw === "string" && raw.length > 120)) {
      addError(errors, `properties.${key}`, "must be a bounded scalar");
      continue;
    }
    result[key] = raw as string | number | boolean;
  }
  return result;
}

export function parseSiteAnalyticsPayload(raw: unknown):
  | { ok: true; event: SiteAnalyticsEvent }
  | { ok: false; errors: Record<string, string> } {
  const errors: Record<string, string> = {};
  if (!isRecord(raw)) return { ok: false, errors: { form: "payload must be an object" } };

  const allowed = new Set(["eventId", "eventName", "occurredAt", "anonymousId", "sessionId", "page", "source", "properties", "performance", "context"]);
  for (const key of Object.keys(raw)) {
    if (!allowed.has(key)) addError(errors, key, "field is not allowlisted");
  }

  const eventId = typeof raw.eventId === "string" && UUID_PATTERN.test(raw.eventId) ? raw.eventId : undefined;
  if (!eventId) addError(errors, "eventId", "must be a UUIDv4");
  const eventName = typeof raw.eventName === "string" && (SITE_ANALYTICS_EVENTS as readonly string[]).includes(raw.eventName)
    ? raw.eventName as SiteAnalyticsEventName
    : undefined;
  if (!eventName) addError(errors, "eventName", "event is not allowlisted");
  const occurredAt = typeof raw.occurredAt === "string" && !Number.isNaN(Date.parse(raw.occurredAt)) ? raw.occurredAt : undefined;
  if (!occurredAt) addError(errors, "occurredAt", "must be an ISO date");
  const anonymousId = optionalString(raw.anonymousId, "anonymousId", errors, 128);
  const sessionId = optionalString(raw.sessionId, "sessionId", errors, 128);
  if (!anonymousId) addError(errors, "anonymousId", "is required");
  if (!sessionId) addError(errors, "sessionId", "is required");

  const page = isRecord(raw.page) ? raw.page : {};
  const path = typeof page.path === "string" && /^\/[\w\-./?=&%#]*$/.test(page.path) ? page.path : undefined;
  if (!path) addError(errors, "page.path", "must be a site-relative path");
  const title = optionalString(page.title, "page.title", errors);
  const referrer = optionalString(page.referrer, "page.referrer", errors, 500);

  const source = isRecord(raw.source) ? raw.source : {};
  const utmSource = optionalString(source.utmSource, "source.utmSource", errors, 80);
  const utmMedium = optionalString(source.utmMedium, "source.utmMedium", errors, 80);
  const utmCampaign = optionalString(source.utmCampaign, "source.utmCampaign", errors, 120);
  const hostname = optionalString(source.hostname, "source.hostname", errors, 120);

  const performance = isRecord(raw.performance) ? raw.performance : {};
  const durationMs = performance.durationMs === undefined || performance.durationMs === null ? undefined : performance.durationMs;
  const statusCode = performance.statusCode === undefined || performance.statusCode === null ? undefined : performance.statusCode;
  if (durationMs !== undefined && (typeof durationMs !== "number" || !Number.isFinite(durationMs) || durationMs < 0 || durationMs > 120000)) addError(errors, "performance.durationMs", "must be a bounded number");
  if (statusCode !== undefined && (typeof statusCode !== "number" || !Number.isInteger(statusCode) || statusCode < 100 || statusCode > 599)) addError(errors, "performance.statusCode", "must be an HTTP status code");

  const context = isRecord(raw.context) ? raw.context : {};
  const viewport = optionalString(context.viewport, "context.viewport", errors, 40);
  const deviceType = optionalString(context.deviceType, "context.deviceType", errors, 30);
  const userAgentFamily = optionalString(context.userAgentFamily, "context.userAgentFamily", errors, 40);
  const properties = validateProperties(raw.properties, errors);

  if (Object.keys(errors).length) return { ok: false, errors };
  return {
    ok: true,
    event: {
      eventId: eventId!, eventName: eventName!, occurredAt: occurredAt!, anonymousId: anonymousId!, sessionId: sessionId!,
      page: { path: path!, ...(title === undefined ? {} : { title }), ...(referrer === undefined ? {} : { referrer }) },
      source: { ...(utmSource === undefined ? {} : { utmSource }), ...(utmMedium === undefined ? {} : { utmMedium }), ...(utmCampaign === undefined ? {} : { utmCampaign }), ...(hostname === undefined ? {} : { hostname }) },
      properties,
      performance: { ...(durationMs === undefined ? {} : { durationMs }), ...(statusCode === undefined ? {} : { statusCode }) },
      context: { ...(viewport === undefined ? {} : { viewport }), ...(deviceType === undefined ? {} : { deviceType }), ...(userAgentFamily === undefined ? {} : { userAgentFamily }) },
    },
  };
}

export function toSiteAnalyticsRecord(event: SiteAnalyticsEvent) {
  return {
    eventId: event.eventId,
    eventName: event.eventName,
    occurredAt: event.occurredAt,
    anonymousId: event.anonymousId,
    sessionId: event.sessionId,
    path: event.page.path,
    title: event.page.title ?? null,
    referrer: event.page.referrer ?? null,
    utmSource: event.source.utmSource ?? null,
    utmMedium: event.source.utmMedium ?? null,
    utmCampaign: event.source.utmCampaign ?? null,
    hostname: event.source.hostname ?? null,
    propertiesJson: JSON.stringify(event.properties),
    durationMs: event.performance.durationMs ?? null,
    statusCode: event.performance.statusCode ?? null,
    viewport: event.context.viewport ?? null,
    deviceType: event.context.deviceType ?? null,
    userAgentFamily: event.context.userAgentFamily ?? null,
  };
}
