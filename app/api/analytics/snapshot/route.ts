import { NextResponse } from "next/server";
import { buildDashboardSnapshot } from "../../../../lib/analytics/site-aggregates";
import { parseSiteAnalyticsPayload } from "../../../../lib/analytics/site";
import type { DashboardLeadRecord } from "../../../../lib/analytics/site-aggregates";

type SnapshotDependencies = {
  readEvents: () => Promise<unknown[]>;
  readLeads: () => Promise<DashboardLeadRecord[]>;
  dashboardKey: string | null;
};

const PRIVATE_HEADERS = {
  "cache-control": "private, no-store",
};

const ONE_DAY_MS = 24 * 60 * 60 * 1000;
const MAX_RECENT_EVENTS = 1000;

const readRecentEvents = async () => {
  const [{ desc, gte }, { getDb }, { siteAnalyticsEvents }] = await Promise.all([
    import("drizzle-orm"),
    import("../../../../db"),
    import("../../../../db/schema"),
  ]);
  const cutoff = new Date(Date.now() - ONE_DAY_MS).toISOString();
  return getDb()
    .select()
    .from(siteAnalyticsEvents)
    .where(gte(siteAnalyticsEvents.occurredAt, cutoff))
    .orderBy(desc(siteAnalyticsEvents.occurredAt))
    .limit(MAX_RECENT_EVENTS)
    .all();
};

const readRecentLeads = async (): Promise<DashboardLeadRecord[]> => {
  const [{ desc }, { getDb }, { assessmentRecords }] = await Promise.all([
    import("drizzle-orm"),
    import("../../../../db"),
    import("../../../../db/schema"),
  ]);
  return getDb()
    .select({
      id: assessmentRecords.id,
      createdAt: assessmentRecords.createdAt,
      name: assessmentRecords.name,
      workEmail: assessmentRecords.workEmail,
      company: assessmentRecords.company,
      role: assessmentRecords.role,
      overallScore: assessmentRecords.overallScore,
      scoreConfidence: assessmentRecords.scoreConfidence,
      impactConfidence: assessmentRecords.impactConfidence,
      estimateType: assessmentRecords.estimateType,
      leadRoute: assessmentRecords.leadRoute,
      riskCodesJson: assessmentRecords.riskCodesJson,
      reportDeliveryStatus: assessmentRecords.reportDeliveryStatus,
      internalNotificationStatus: assessmentRecords.internalNotificationStatus,
    })
    .from(assessmentRecords)
    .orderBy(desc(assessmentRecords.createdAt))
    .limit(50)
    .all();
};

const getDashboardKey = async () => {
  const { env } = await import("cloudflare:workers");
  return typeof env.ANALYTICS_DASHBOARD_KEY === "string"
    ? env.ANALYTICS_DASHBOARD_KEY
    : null;
};

function isAuthorized(request: Request, key: string | null) {
  if (!key) return false;
  const url = new URL(request.url);
  return request.headers.get("x-runrate-dashboard-key") === key || url.searchParams.get("key") === key;
}

function parseAnalyticsRows(rawEvents: unknown[]) {
  return rawEvents.flatMap((raw) => {
    if (raw && typeof raw === "object" && "propertiesJson" in raw) {
      const row = raw as Record<string, unknown>;
      let properties: Record<string, unknown> = {};
      try {
        const parsed = JSON.parse(String(row.propertiesJson || "{}"));
        properties = parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
      } catch {
        properties = {};
      }
      const parsed = parseSiteAnalyticsPayload({
        eventId: row.eventId,
        eventName: row.eventName,
        occurredAt: row.occurredAt,
        anonymousId: row.anonymousId,
        sessionId: row.sessionId,
        page: {
          path: row.path,
          title: row.title ?? undefined,
          referrer: row.referrer ?? undefined,
        },
        source: {
          utmSource: row.utmSource ?? undefined,
          utmMedium: row.utmMedium ?? undefined,
          utmCampaign: row.utmCampaign ?? undefined,
          hostname: row.hostname ?? undefined,
        },
        properties,
        performance: {
          durationMs: row.durationMs ?? undefined,
          statusCode: row.statusCode ?? undefined,
        },
        context: {
          viewport: row.viewport ?? undefined,
          deviceType: row.deviceType ?? undefined,
          userAgentFamily: row.userAgentFamily ?? undefined,
        },
      });
      return parsed.ok ? [parsed.event] : [];
    }
    const parsed = parseSiteAnalyticsPayload(raw);
    return parsed.ok ? [parsed.event] : [];
  });
}

export function createAnalyticsSnapshotHandler(
  dependencies: Partial<SnapshotDependencies> = {},
) {
  return async function getAnalyticsSnapshot(request: Request) {
    const dashboardKey = dependencies.dashboardKey ?? await getDashboardKey().catch(() => null);
    if (!isAuthorized(request, dashboardKey)) {
      return NextResponse.json(
        { error: "Analytics dashboard is not authorized." },
        {
          status: dashboardKey ? 401 : 503,
          headers: PRIVATE_HEADERS,
        },
      );
    }

    try {
      const [rawEvents, leads] = await Promise.all([
        (dependencies.readEvents ?? readRecentEvents)(),
        (dependencies.readLeads ?? readRecentLeads)(),
      ]);
      return NextResponse.json(
        buildDashboardSnapshot(parseAnalyticsRows(rawEvents), leads),
        { headers: PRIVATE_HEADERS },
      );
    } catch {
      return NextResponse.json(
        { error: "Analytics snapshot unavailable." },
        { status: 503, headers: PRIVATE_HEADERS },
      );
    }
  };
}

export const GET = createAnalyticsSnapshotHandler();
