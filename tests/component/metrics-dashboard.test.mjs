import assert from "node:assert/strict";
import test from "node:test";
import "./setup.mjs";
import React from "react";
import { render, screen } from "@testing-library/react";
import MetricsDashboard from "../../components/MetricsDashboard.tsx";

test("MetricsDashboard renders lead follow-up metrics and sales triage sections", () => {
  render(React.createElement(MetricsDashboard));

  assert.ok(screen.getByText("Lead follow-up dashboard"));
  assert.ok(screen.getByText("Known high-intent leads"));
  assert.ok(screen.getByText("Follow-up queue"));
  assert.ok(screen.getByText("Assessment funnel"));
  assert.ok(screen.getByText("Lead-fit context"));
  assert.ok(screen.getByText("Lead scoring context"));
  assert.ok(screen.getByText("Drop-off and delivery risk"));
  assert.ok(screen.getByText("Recent events"));
});
