import type { SiteAnalyticsEvent } from "./site";

export type DashboardLeadRecord = {
  id: string;
  createdAt: string;
  name?: string | null;
  workEmail?: string | null;
  company?: string | null;
  role?: string | null;
  overallScore?: number | null;
  scoreConfidence?: string | null;
  impactConfidence?: string | null;
  estimateType?: string | null;
  leadRoute?: string | null;
  riskCodesJson?: string | null;
  reportDeliveryStatus?: string | null;
  internalNotificationStatus?: string | null;
};

export type DashboardSnapshot = {
  activeUsers: number;
  pageviewsToday: number;
  assessmentStarts: number;
  assessmentCompletions: number;
  contactSubmits: number;
  downloadsToday: number;
  qualifiedLeadActionsToday: number;
  knownHighIntentLeads: number;
  repeatVisitors: number;
  formAbandons: number;
  ctaClicksWithoutSubmit: number;
  errorRate: number;
  apiLatencyP95: number;
  line: Array<{ label: string; pageviews: number; activeUsers: number }>;
  topPages: Array<{ path: string; views: number }>;
  sources: Array<{ label: string; count: number }>;
  funnel: Array<{ label: string; count: number }>;
  followUpQueue: Array<{ label: string; company: string; role: string; priority: string; trigger: string; score: number | null; action: string; time: string }>;
  leadFit: Array<{ label: string; value: string | number; action: string }>;
  assessmentIntelligence: Array<{ label: string; value: string | number; action: string }>;
  conversionFriction: Array<{ label: string; value: string | number; action: string }>;
  highIntentSignals: Array<{ label: string; value: string | number; action: string }>;
  recentEvents: Array<{ time: string; event: string; detail: string }>;
};

const funnelLabels = ["Assessment viewed", "Business context completed", "Preliminary result", "Contact gate", "Full result"];

function sameUtcDay(value: string, now: Date) {
  const date = new Date(value);
  return date.getUTCFullYear() === now.getUTCFullYear() && date.getUTCMonth() === now.getUTCMonth() && date.getUTCDate() === now.getUTCDate();
}

function property(event: SiteAnalyticsEvent, key: string) {
  return event.properties[key];
}

function countBy<T>(values: T[]) {
  const counts = new Map<T, number>();
  for (const value of values) counts.set(value, (counts.get(value) ?? 0) + 1);
  return counts;
}

function toTopRows(counts: Map<string, number>, key: "path" | "label") {
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10).map(([value, count]) => ({ [key]: value, ...(key === "path" ? { views: count } : { count }) })) as never;
}

export function buildDashboardSnapshot(events: SiteAnalyticsEvent[], leadsOrNow: DashboardLeadRecord[] | Date = []) : DashboardSnapshot {
  const now = leadsOrNow instanceof Date ? leadsOrNow : new Date();
  const leads = Array.isArray(leadsOrNow) ? leadsOrNow : [];
  const today = events.filter((event) => sameUtcDay(event.occurredAt, now));
  const pageviews = today.filter((event) => event.eventName === "page_view");
  const activeCutoff = now.getTime() - 5 * 60 * 1000;
  const activeSessions = new Set(events.filter((event) => ["page_view", "session_heartbeat"].includes(event.eventName) && new Date(event.occurredAt).getTime() >= activeCutoff).map((event) => event.sessionId));
  const apiEvents = today.filter((event) => ["api_error", "api_latency"].includes(event.eventName));
  const errors = apiEvents.filter((event) => event.eventName === "api_error");
  const latencies = apiEvents.map((event) => event.performance.durationMs).filter((value): value is number => typeof value === "number").sort((a, b) => a - b);
  const p95 = latencies.length ? latencies[Math.min(latencies.length - 1, Math.ceil(latencies.length * 0.95) - 1)] : 0;
  const eventByName = (name: SiteAnalyticsEvent["eventName"]) => today.filter((event) => event.eventName === name);
  const assessmentStarts = today.filter((event) => event.eventName === "assessment_step_view" && property(event, "step") === "landing").length;
  const completions = today.filter((event) => event.eventName === "assessment_step_complete" && property(event, "step") === "full-result").length;
  const contactSubmits = today.filter((event) => event.eventName === "form_submit" && property(event, "formId") === "contact").length;
  const downloadsToday = eventByName("download_click").length;
  const sessionCounts = countBy(pageviews.map((event) => event.sessionId));
  const repeatVisitors = [...sessionCounts.values()].filter((count) => count > 1).length;

  const funnelCounts = [
    assessmentStarts,
    today.filter((event) => event.eventName === "assessment_step_complete" && property(event, "step") === "context").length,
    today.filter((event) => event.eventName === "assessment_step_view" && property(event, "step") === "preliminary").length,
    today.filter((event) => event.eventName === "assessment_step_view" && property(event, "step") === "contact-gate").length,
    completions,
  ];
  const pageCounts = countBy(pageviews.map((event) => event.page.path));
  const sourceCounts = countBy(pageviews.map((event) => event.source.utmSource ?? (new URL(event.page.referrer ?? "https://direct.invalid").hostname.replace(/^www\./, "") || "direct")));
  const recentBuckets = Array.from({ length: 6 }, (_, index) => {
    const end = now.getTime() - (5 - index) * 5 * 60 * 1000;
    const start = end - 5 * 60 * 1000;
    const bucket = events.filter((event) => { const time = new Date(event.occurredAt).getTime(); return time >= start && time < end; });
    return { label: new Date(end).toISOString().slice(11, 16), pageviews: bucket.filter((event) => event.eventName === "page_view").length, activeUsers: new Set(bucket.filter((event) => ["page_view", "session_heartbeat"].includes(event.eventName)).map((event) => event.sessionId)).size };
  });

  const followUpQueue = leads.slice(0, 20).map((lead) => {
    const score = typeof lead.overallScore === "number" ? lead.overallScore : null;
    const priority = score !== null && score < 50 ? "High" : score !== null && score < 75 ? "Medium" : "Review";
    return { label: lead.name || lead.workEmail || "Unknown lead", company: lead.company || "Unknown company", role: lead.role || "Unknown role", priority, trigger: lead.leadRoute || "Assessment completed", score, action: lead.reportDeliveryStatus === "sent" ? "Review and follow up" : "Resolve report delivery", time: lead.createdAt };
  });
  const highIntentLeads = leads.filter((lead) => lead.leadRoute === "diagnostic" || (lead.overallScore ?? 0) < 60).length;
  const recentEvents = [...events].sort((a, b) => b.occurredAt.localeCompare(a.occurredAt)).slice(0, 20).map((event) => ({ time: event.occurredAt, event: event.eventName, detail: event.page.path }));

  return {
    activeUsers: activeSessions.size,
    pageviewsToday: pageviews.length,
    assessmentStarts,
    assessmentCompletions: completions,
    contactSubmits,
    downloadsToday,
    qualifiedLeadActionsToday: completions + contactSubmits + downloadsToday,
    knownHighIntentLeads: highIntentLeads,
    repeatVisitors,
    formAbandons: eventByName("form_abandon").length,
    ctaClicksWithoutSubmit: 0,
    errorRate: apiEvents.length ? Math.round((errors.length / apiEvents.length) * 100) : 0,
    apiLatencyP95: p95,
    line: recentBuckets,
    topPages: toTopRows(pageCounts, "path"),
    sources: toTopRows(sourceCounts, "label"),
    funnel: funnelLabels.map((label, index) => ({ label, count: funnelCounts[index] })),
    followUpQueue,
    leadFit: leads.length ? [{ label: "Known assessment leads", value: leads.length, action: "Review the follow-up queue." }] : [],
    assessmentIntelligence: leads.length ? [{ label: "Diagnostic-fit leads", value: highIntentLeads, action: "Prioritize high-intent diagnostic conversations." }] : [],
    conversionFriction: [{ label: "Form abandons", value: eventByName("form_abandon").length, action: "Inspect fields with repeated abandonment." }],
    highIntentSignals: [{ label: "Assessment completions", value: completions, action: "Follow up while intent is fresh." }, { label: "Downloads", value: downloadsToday, action: "Review resource engagement." }],
    recentEvents,
  };
}
