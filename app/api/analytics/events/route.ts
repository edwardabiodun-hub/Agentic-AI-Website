import { NextResponse } from "next/server";
import type { siteAnalyticsEvents } from "../../../../db/schema";
import {
  parseSiteAnalyticsPayload,
  toSiteAnalyticsRecord,
} from "../../../../lib/analytics/site";

type SiteAnalyticsEventRecord = typeof siteAnalyticsEvents.$inferInsert;
type HandlerDependencies = {
  persistEvent: (record: SiteAnalyticsEventRecord) => Promise<void>;
};

const PRIVATE_HEADERS = {
  "cache-control": "private, no-store",
};

const persistSiteAnalyticsEvent = async (record: SiteAnalyticsEventRecord) => {
  const [{ getDb }, { siteAnalyticsEvents }] = await Promise.all([
    import("../../../../db"),
    import("../../../../db/schema"),
  ]);
  await getDb().insert(siteAnalyticsEvents).values(record);
};

export function createSiteAnalyticsEventHandler(
  dependencies: Partial<HandlerDependencies> = {},
) {
  const persistEvent = dependencies.persistEvent ?? persistSiteAnalyticsEvent;

  return async function postSiteAnalyticsEvent(request: Request) {
    const parsed = parseSiteAnalyticsPayload(
      await request.json().catch(() => null),
    );
    if (!parsed.ok) {
      return NextResponse.json(parsed, {
        status: 422,
        headers: PRIVATE_HEADERS,
      });
    }

    const record = toSiteAnalyticsRecord(parsed.event);
    let persistenceAvailable = true;
    try {
      await persistEvent(record);
    } catch {
      persistenceAvailable = false;
    }

    return NextResponse.json(
      { ok: true, persistenceAvailable },
      { status: 202, headers: PRIVATE_HEADERS },
    );
  };
}

export const POST = createSiteAnalyticsEventHandler();
