"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { DashboardSnapshot } from "../lib/analytics/site-aggregates";

const emptySnapshot: DashboardSnapshot = {
  activeUsers: 0,
  pageviewsToday: 0,
  assessmentStarts: 0,
  assessmentCompletions: 0,
  contactSubmits: 0,
  downloadsToday: 0,
  qualifiedLeadActionsToday: 0,
  knownHighIntentLeads: 0,
  repeatVisitors: 0,
  formAbandons: 0,
  ctaClicksWithoutSubmit: 0,
  errorRate: 0,
  apiLatencyP95: 0,
  line: [],
  topPages: [],
  sources: [],
  funnel: [
    { label: "Assessment viewed", count: 0 },
    { label: "Business context completed", count: 0 },
    { label: "Preliminary result", count: 0 },
    { label: "Contact gate", count: 0 },
    { label: "Full result", count: 0 },
  ],
  followUpQueue: [],
  leadFit: [],
  assessmentIntelligence: [],
  conversionFriction: [],
  highIntentSignals: [],
  recentEvents: [],
};

const formatPercent = (value: number) => `${Math.round(value)}%`;

function StatCard({ label, value, helper }: { label: string; value: string | number; helper: string }) {
  return (
    <section className="metric-card" aria-label={label}>
      <p className="eyebrow">{label}</p>
      <strong>{value}</strong>
      <span>{helper}</span>
    </section>
  );
}

function BarList({ rows, valueLabel }: { rows: Array<{ label?: string; path?: string; count?: number; views?: number }>; valueLabel: "count" | "views" }) {
  const max = Math.max(1, ...rows.map((row) => Number(row[valueLabel] ?? 0)));
  return (
    <div className="metric-bars">
      {rows.length === 0 ? <p>No events yet.</p> : rows.map((row) => {
        const label = row.label ?? row.path ?? "Unknown";
        const value = Number(row[valueLabel] ?? 0);
        return (
          <div className="metric-bar-row" key={label}>
            <span>{label}</span>
            <div aria-hidden="true"><i style={{ width: `${Math.max(6, (value / max) * 100)}%` }} /></div>
            <strong>{value}</strong>
          </div>
        );
      })}
    </div>
  );
}

function InsightList({ rows }: { rows: Array<{ label: string; value: string | number; action: string }> }) {
  return (
    <div className="metric-insight-list">
      {rows.length === 0 ? <p>No signals yet.</p> : rows.map((row) => (
        <article key={row.label} className="metric-insight">
          <span>{row.label}</span>
          <strong>{row.value}</strong>
          <p>{row.action}</p>
        </article>
      ))}
    </div>
  );
}

export default function MetricsDashboard() {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot>(emptySnapshot);
  const [status, setStatus] = useState(() => {
    if (typeof window === "undefined") return "Waiting for dashboard snapshot";
    return window.sessionStorage.getItem("runrate_metrics_key")
      ? "Waiting for dashboard snapshot"
      : "Dashboard key required.";
  });
  const [keyVersion, setKeyVersion] = useState(0);
  const hasReceivedSnapshotRef = useRef(false);
  const peakLineValue = useMemo(
    () => Math.max(1, ...snapshot.line.map((point) => Math.max(point.pageviews, point.activeUsers))),
    [snapshot.line],
  );

  useEffect(() => {
    const dashboardKey = window.sessionStorage.getItem("runrate_metrics_key") ?? window.prompt("Enter the RunRate metrics dashboard key");
    if (!dashboardKey) {
      return;
    }
    window.sessionStorage.setItem("runrate_metrics_key", dashboardKey);

    const controller = new AbortController();
    let stopped = false;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    const fetchSnapshot = async () => {
      try {
        const response = await fetch("/api/analytics/snapshot", {
          headers: {
            "x-runrate-dashboard-key": dashboardKey,
          },
          cache: "no-store",
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Snapshot request failed with status ${response.status}`);
        }
        setSnapshot(await response.json());
        hasReceivedSnapshotRef.current = true;
        setStatus("Dashboard refreshed");
      } catch {
        if (!stopped) {
          if (!hasReceivedSnapshotRef.current) {
            setStatus("Snapshot unavailable. Check the dashboard key or Cloudflare environment.");
          } else {
            setStatus("Dashboard refresh delayed");
          }
        }
      } finally {
        if (!stopped) {
          timeoutId = setTimeout(fetchSnapshot, 15_000);
        }
      }
    };

    void fetchSnapshot();

    return () => {
      stopped = true;
      controller.abort();
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [keyVersion]);

  const resetDashboardKey = () => {
    window.sessionStorage.removeItem("runrate_metrics_key");
    hasReceivedSnapshotRef.current = false;
    setStatus("Waiting for dashboard snapshot");
    setKeyVersion((version) => version + 1);
  };

  return (
    <main className="metrics-shell">
      <section className="metrics-hero">
        <p className="eyebrow">RunRate internal dashboard</p>
        <h1>Lead follow-up dashboard</h1>
        <p>
          Prioritize high-intent actions, known lead context, assessment intelligence, and conversion friction
          so follow-up happens while intent is still fresh.
        </p>
        <div className="metrics-status-row">
          <span className="metrics-status">{status}</span>
          <button className="metrics-key-button" type="button" onClick={resetDashboardKey}>
            Change dashboard key
          </button>
        </div>
      </section>

      <section className="metrics-grid" aria-label="Website metric summary">
        <StatCard label="Known high-intent leads" value={snapshot.knownHighIntentLeads} helper="Diagnostic-fit leads today" />
        <StatCard label="Qualified actions" value={snapshot.qualifiedLeadActionsToday} helper="Completions, submits, downloads" />
        <StatCard label="Assessment completions" value={snapshot.assessmentCompletions} helper="Full-result events today" />
        <StatCard label="Contact submits" value={snapshot.contactSubmits} helper="Direct conversation requests" />
        <StatCard label="Repeat visitors" value={snapshot.repeatVisitors} helper="Multiple pageviews in session" />
        <StatCard label="Capture health" value={formatPercent(100 - snapshot.errorRate)} helper={`API p95 ${snapshot.apiLatencyP95}ms`} />
      </section>

      <section className="metrics-panel metric-priority-panel">
        <div>
          <p className="eyebrow">Immediate action triggers</p>
          <h2>Follow-up queue</h2>
        </div>
        <div className="metric-lead-table">
          {snapshot.followUpQueue.length === 0 ? <p>No known assessment leads yet.</p> : snapshot.followUpQueue.map((lead) => (
            <article key={`${lead.label}-${lead.time}`} className="metric-lead-row">
              <div>
                <strong>{lead.label}</strong>
                <span>{lead.company} · {lead.role}</span>
              </div>
              <div>
                <span className="metric-priority">{lead.priority}</span>
                <small>{lead.trigger}{lead.score == null ? "" : ` · ${lead.score}/100`}</small>
              </div>
              <p>{lead.action}</p>
              <time>{lead.time}</time>
            </article>
          ))}
        </div>
      </section>

      <section className="metrics-panel">
        <div>
          <p className="eyebrow">Last 30 minutes</p>
          <h2>Live engagement trend</h2>
        </div>
        <div className="metric-line" role="img" aria-label="Recent pageviews and active users by five-minute interval">
          {snapshot.line.length === 0 ? <p>No trend events yet.</p> : snapshot.line.map((point) => (
            <div className="metric-line-column" key={point.label}>
              <span style={{ height: `${Math.max(8, (point.pageviews / peakLineValue) * 100)}%` }} />
              <i style={{ height: `${Math.max(8, (point.activeUsers / peakLineValue) * 100)}%` }} />
              <small>{point.label}</small>
            </div>
          ))}
        </div>
      </section>

      <section className="metrics-two-column">
        <div className="metrics-panel">
          <p className="eyebrow">Engagement and qualification</p>
          <h2>Assessment funnel</h2>
          <BarList rows={snapshot.funnel} valueLabel="count" />
        </div>
        <div className="metrics-panel">
          <p className="eyebrow">High-intent behavior</p>
          <h2>Action signals</h2>
          <InsightList rows={snapshot.highIntentSignals} />
        </div>
      </section>

      <section className="metrics-two-column">
        <div className="metrics-panel">
          <p className="eyebrow">Firmographic and identity</p>
          <h2>Lead-fit context</h2>
          <InsightList rows={snapshot.leadFit} />
        </div>
        <div className="metrics-panel">
          <p className="eyebrow">Assessment intelligence</p>
          <h2>Lead scoring context</h2>
          <InsightList rows={snapshot.assessmentIntelligence} />
        </div>
      </section>

      <section className="metrics-two-column">
        <div className="metrics-panel">
          <p className="eyebrow">Conversion friction</p>
          <h2>Drop-off and delivery risk</h2>
          <InsightList rows={snapshot.conversionFriction} />
        </div>
        <div className="metrics-panel">
          <p className="eyebrow">Supporting traffic context</p>
          <h2>Sources and pages</h2>
          <BarList rows={snapshot.sources} valueLabel="count" />
          <hr className="metric-divider" />
          <BarList rows={snapshot.topPages} valueLabel="views" />
        </div>
      </section>

      <section className="metrics-panel">
        <p className="eyebrow">Operations</p>
        <h2>Recent events</h2>
        <ul className="metric-events">
          {snapshot.recentEvents.length === 0 ? <li>No events yet.</li> : snapshot.recentEvents.map((event, index) => (
            <li key={`${event.time}-${event.event}-${index}`}>
              <span>{event.time}</span>
              <strong>{event.event}</strong>
              <em>{event.detail}</em>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
