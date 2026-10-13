import { buildDashboardSnapshot } from "../../../../lib/analytics/site-aggregates";
import { parseSiteAnalyticsPayload } from "../../../../lib/analytics/site";
import type { DashboardLeadRecord } from "../../../../lib/analytics/site-aggregates";

type StreamDependencies = {
  readEvents: () => Promise<unknown[]>;
  readLeads: () => Promise<DashboardLeadRecord[]>;
  dashboardKey: string | null;
  refreshMs: number;
};

const readRecentEvents = async () => {
  const [{ getDb }, { siteAnalyticsEvents }] = await Promise.all([
    import("../../../../db"),
    import("../../../../db/schema"),
  ]);
  return getDb().select().from(siteAnalyticsEvents).all();
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

export function createAnalyticsStreamHandler(
  dependencies: Partial<StreamDependencies> = {},
) {
  return async function getAnalyticsStream(request: Request) {
    const dashboardKey = dependencies.dashboardKey ?? await getDashboardKey().catch(() => null);
    if (!isAuthorized(request, dashboardKey)) {
      return new Response("Analytics dashboard is not authorized.", {
        status: dashboardKey ? 401 : 503,
        headers: { "cache-control": "private, no-store" },
      });
    }

    const encoder = new TextEncoder();
    const refreshMs = dependencies.refreshMs ?? 10_000;
    const readEvents = dependencies.readEvents ?? readRecentEvents;
    const readLeads = dependencies.readLeads ?? readRecentLeads;
    let closed = false;
    request.signal.addEventListener("abort", () => {
      closed = true;
    });

    const sendSnapshot = async (controller: ReadableStreamDefaultController<Uint8Array>) => {
      const rawEvents = await readEvents();
      const leads = await readLeads();
      const events = rawEvents.flatMap((raw) => {
        if (raw && typeof raw === "object" && "propertiesJson" in raw) {
          const row = raw as Record<string, unknown>;
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
            properties: JSON.parse(String(row.propertiesJson || "{}")),
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
      controller.enqueue(
        encoder.encode(`data: ${JSON.stringify(buildDashboardSnapshot(events, leads))}\n\n`),
      );
    };

    const stream = new ReadableStream({
      async start(controller) {
        while (!closed) {
          await sendSnapshot(controller);
          await new Promise((resolve) => setTimeout(resolve, refreshMs));
        }
        controller.close();
      },
      cancel() {
        closed = true;
      },
    });

    return new Response(stream, {
      headers: {
        "content-type": "text/event-stream",
        "cache-control": "private, no-store",
        connection: "keep-alive",
      },
    });
  };
}

export const GET = createAnalyticsStreamHandler();
