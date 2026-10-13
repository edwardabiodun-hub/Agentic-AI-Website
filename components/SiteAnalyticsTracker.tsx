"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import {
  installSiteAnalyticsTracking,
  trackSiteAnalyticsEvent,
} from "../lib/analytics/site-track";

export function SiteAnalyticsTracker() {
  const pathname = usePathname();

  useEffect(() => {
    installSiteAnalyticsTracking();
  }, []);

  useEffect(() => {
    trackSiteAnalyticsEvent("page_view");
  }, [pathname]);

  return null;
}
