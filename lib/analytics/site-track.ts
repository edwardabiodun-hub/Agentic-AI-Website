import { SITE_ANALYTICS_EVENTS, type SiteAnalyticsEventName } from "./site";

const ANONYMOUS_KEY = "runrate_analytics_anonymous_id";
const SESSION_KEY = "runrate_analytics_session_id";

function identifier(key: string) {
  try {
    const storage = window.localStorage;
    const existing = storage.getItem(key);
    if (existing) return existing;
    const value = crypto.randomUUID();
    storage.setItem(key, value);
    return value;
  } catch {
    return crypto.randomUUID();
  }
}

function sessionIdentifier() {
  try {
    const storage = window.sessionStorage;
    const existing = storage.getItem(SESSION_KEY);
    if (existing) return existing;
    const value = crypto.randomUUID();
    storage.setItem(SESSION_KEY, value);
    return value;
  } catch {
    return crypto.randomUUID();
  }
}

export function trackSiteAnalyticsEvent(eventName: SiteAnalyticsEventName, properties: Record<string, string | number | boolean> = {}, performance: { durationMs?: number; statusCode?: number } = {}) {
  if (typeof window === "undefined" || typeof document === "undefined") return;
  if (!(SITE_ANALYTICS_EVENTS as readonly string[]).includes(eventName)) return;
  const url = new URL(window.location.href);
  const payload = {
    eventId: crypto.randomUUID(),
    eventName,
    occurredAt: new Date().toISOString(),
    anonymousId: identifier(ANONYMOUS_KEY),
    sessionId: sessionIdentifier(),
    page: { path: window.location.pathname, title: document.title, referrer: document.referrer || undefined },
    source: { utmSource: url.searchParams.get("utm_source") || undefined, utmMedium: url.searchParams.get("utm_medium") || undefined, utmCampaign: url.searchParams.get("utm_campaign") || undefined, hostname: window.location.hostname },
    properties,
    performance,
    context: { viewport: `${window.innerWidth}x${window.innerHeight}`, deviceType: window.innerWidth < 768 ? "mobile" : "desktop", userAgentFamily: navigator.userAgent.includes("Chrome") ? "Chromium" : undefined },
  };
  const body = JSON.stringify(payload);
  if (navigator.sendBeacon) {
    navigator.sendBeacon("/api/analytics/events", new Blob([body], { type: "application/json" }));
    return;
  }
  void fetch("/api/analytics/events", { method: "POST", headers: { "content-type": "application/json" }, body, keepalive: true }).catch(() => undefined);
}

export function installSiteAnalyticsTracking() {
  if (typeof window === "undefined") return () => undefined;
  const heartbeat = window.setInterval(() => trackSiteAnalyticsEvent("session_heartbeat"), 60_000);
  return () => window.clearInterval(heartbeat);
}
