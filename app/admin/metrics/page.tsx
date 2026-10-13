import { headers } from "next/headers";
import { notFound } from "next/navigation";
import MetricsDashboard from "../../../components/MetricsDashboard";
import { isAuthorizedAdminEmail } from "../../../lib/admin/access";

export const metadata = {
  title: "Live Website Metrics",
  robots: {
    index: false,
    follow: false,
  },
};

export const dynamic = "force-dynamic";

const getConfiguredAdminEmail = async () => {
  try {
    const { env } = await import("cloudflare:workers");
    return typeof env.ADMIN_EMAIL === "string" ? env.ADMIN_EMAIL : null;
  } catch {
    return process.env.ADMIN_EMAIL ?? null;
  }
};

export default async function MetricsPage() {
  const requestHeaders = await headers();
  const adminEmail = await getConfiguredAdminEmail();
  if (!isAuthorizedAdminEmail(requestHeaders, adminEmail)) {
    notFound();
  }

  return <MetricsDashboard />;
}
