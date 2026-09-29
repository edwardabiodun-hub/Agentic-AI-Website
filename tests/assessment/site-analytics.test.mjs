import assert from "node:assert/strict";
import test from "node:test";
import {
  parseSiteAnalyticsPayload,
  SITE_ANALYTICS_EVENTS,
} from "../../lib/analytics/site.ts";
import {
  buildDashboardSnapshot,
} from "../../lib/analytics/site-aggregates.ts";
import { createSiteAnalyticsEventHandler } from "../../app/api/analytics/events/route.ts";
import { createAnalyticsSnapshotHandler } from "../../app/api/analytics/snapshot/route.ts";

const validEvent = (overrides = {}) => ({
  eventId: "11111111-1111-4111-8111-111111111111",
  eventName: "page_view",
  occurredAt: "2026-08-03T12:00:00.000Z",
  anonymousId: "anonymous-visitor-123",
  sessionId: "session-visitor-123",
  page: {
    path: "/assessment",
    title: "Business Independence Assessment",
    referrer: "https://www.linkedin.com/",
  },
  source: {
    utmSource: "linkedin",
    utmMedium: "social",
    utmCampaign: "diagnostic-launch",
    hostname: "www.runrategroup.com",
  },
  properties: {},
  context: {
    viewport: "1440x900",
    deviceType: "desktop",
    userAgentFamily: "Chromium",
  },
  ...overrides,
});

test("SITE_ANALYTICS_EVENTS exposes the approved website event allowlist", () => {
  assert.deepEqual(SITE_ANALYTICS_EVENTS, [
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
  ]);
});

test("parseSiteAnalyticsPayload accepts a valid compact website event", () => {
  const parsed = parseSiteAnalyticsPayload(validEvent());
  assert.equal(parsed.ok, true);
  assert.equal(parsed.event.eventName, "page_view");
  assert.equal(parsed.event.page.path, "/assessment");
});

for (const forbidden of ["name", "email", "workEmail", "phone", "company", "answers", "notes", "freeText"]) {
  test(`parseSiteAnalyticsPayload rejects forbidden or unrecognized field "${forbidden}"`, () => {
    const parsed = parseSiteAnalyticsPayload(validEvent({ [forbidden]: "private value" }));
    assert.equal(parsed.ok, false);
    assert.ok(parsed.errors[forbidden]);
  });
}

test("parseSiteAnalyticsPayload rejects PII-like analytics properties", () => {
  const parsed = parseSiteAnalyticsPayload(
    validEvent({
      properties: {
        fieldName: "email",
        value: "eddie@example.com",
      },
    }),
  );
  assert.equal(parsed.ok, false);
  assert.ok(parsed.errors["properties.value"]);
});

test("site analytics events route persists only normalized safe columns", async () => {
  let persisted = null;
  const handler = createSiteAnalyticsEventHandler({
    persistEvent: async (record) => {
      persisted = record;
    },
  });
  const response = await handler(new Request("https://example.com/api/analytics/events", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(validEvent({
      properties: {
        formId: "contact",
        fieldName: "timeframe",
      },
    })),
  }));
  assert.equal(response.status, 202);
  assert.equal((await response.json()).ok, true);
  assert.deepEqual(persisted, {
    eventId: "11111111-1111-4111-8111-111111111111",
    eventName: "page_view",
    occurredAt: "2026-08-03T12:00:00.000Z",
    anonymousId: "anonymous-visitor-123",
    sessionId: "session-visitor-123",
    path: "/assessment",
    title: "Business Independence Assessment",
    referrer: "https://www.linkedin.com/",
    utmSource: "linkedin",
    utmMedium: "social",
    utmCampaign: "diagnostic-launch",
    hostname: "www.runrategroup.com",
    propertiesJson: "{\"formId\":\"contact\",\"fieldName\":\"timeframe\"}",
    durationMs: null,
    statusCode: null,
    viewport: "1440x900",
    deviceType: "desktop",
    userAgentFamily: "Chromium",
  });
});

test("buildDashboardSnapshot calculates live traffic, funnel, sources, and system health", () => {
  const now = new Date("2026-08-03T12:10:00.000Z");
  const events = [
    validEvent({ eventId: "11111111-1111-4111-8111-111111111111", eventName: "page_view", sessionId: "s1", occurredAt: "2026-08-03T12:09:40.000Z" }),
    validEvent({ eventId: "22222222-2222-4222-8222-222222222222", eventName: "session_heartbeat", sessionId: "s1", occurredAt: "2026-08-03T12:09:50.000Z" }),
    validEvent({ eventId: "33333333-3333-4333-8333-333333333333", eventName: "assessment_step_view", sessionId: "s2", occurredAt: "2026-08-03T12:06:00.000Z", properties: { step: "landing" } }),
    validEvent({ eventId: "44444444-4444-4444-8444-444444444444", eventName: "assessment_step_complete", sessionId: "s2", occurredAt: "2026-08-03T12:06:30.000Z", properties: { step: "context" } }),
    validEvent({ eventId: "55555555-5555-4555-8555-555555555555", eventName: "download_click", sessionId: "s3", occurredAt: "2026-08-03T12:07:00.000Z", page: { path: "/founder-resources" }, properties: { fileType: "pdf" } }),
    validEvent({ eventId: "66666666-6666-4666-8666-666666666666", eventName: "api_latency", sessionId: "s4", occurredAt: "2026-08-03T12:08:00.000Z", performance: { durationMs: 320, statusCode: 200 } }),
    validEvent({ eventId: "77777777-7777-4777-8777-777777777777", eventName: "api_error", sessionId: "s4", occurredAt: "2026-08-03T12:08:10.000Z", performance: { durationMs: 900, statusCode: 503 } }),
  ];
  const parsedEvents = events.map((event) => {
    const parsed = parseSiteAnalyticsPayload(event);
    assert.equal(parsed.ok, true);
    return parsed.event;
  });

  const snapshot = buildDashboardSnapshot(parsedEvents, now);
  assert.equal(snapshot.activeUsers, 1);
  assert.equal(snapshot.pageviewsToday, 1);
  assert.equal(snapshot.assessmentStarts, 1);
  assert.equal(snapshot.downloadsToday, 1);
  assert.equal(snapshot.errorRate, 50);
  assert.equal(snapshot.apiLatencyP95, 900);
  assert.equal(snapshot.topPages[0].path, "/assessment");
  assert.equal(snapshot.sources[0].label, "linkedin");
  assert.deepEqual(snapshot.funnel.map((step) => step.label), [
    "Assessment viewed",
    "Business context completed",
    "Preliminary result",
    "Contact gate",
    "Full result",
  ]);
});

test("analytics snapshot route returns a bounded one-shot JSON response", async () => {
  let readEventsCalls = 0;
  let readLeadsCalls = 0;
  const handler = createAnalyticsSnapshotHandler({
    dashboardKey: "test-dashboard-key",
    readEvents: async () => {
      readEventsCalls += 1;
      return [
        {
          ...validEvent(),
          occurredAt: new Date().toISOString(),
          propertiesJson: "{}",
          path: "/assessment",
          title: "Business Independence Assessment",
          referrer: "https://www.linkedin.com/",
          utmSource: "linkedin",
          utmMedium: "social",
          utmCampaign: "diagnostic-launch",
          hostname: "www.runrategroup.com",
          durationMs: null,
          statusCode: null,
          viewport: "1440x900",
          deviceType: "desktop",
          userAgentFamily: "Chromium",
        },
      ];
    },
    readLeads: async () => {
      readLeadsCalls += 1;
      return [];
    },
  });

  const response = await handler(new Request("https://example.com/api/analytics/snapshot?key=test-dashboard-key"));

  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /application\/json/);
  assert.notEqual(response.headers.get("content-type"), "text/event-stream");
  const body = await response.json();
  assert.equal(body.pageviewsToday, 1);
  assert.equal(readEventsCalls, 1);
  assert.equal(readLeadsCalls, 1);
});
