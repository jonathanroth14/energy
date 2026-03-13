import { AlertFeed } from "@/components/alerts/alert-feed";
import { KpiRow } from "@/components/dashboard/kpi-row";
import { RightRail } from "@/components/dashboard/right-rail";
import { SectionTitle } from "@/components/ui/section-title";
import { getAlerts, getWatchlists } from "@/lib/api";

export default async function DashboardPage() {
  const [alerts, watchlists] = await Promise.all([getAlerts(), getWatchlists()]);

  const kpis = {
    newAlerts: alerts.length,
    bankruptcyCases: alerts.filter((a) => a.signal_type === "New bankruptcy filing").length,
    productionCollapses: alerts.filter((a) => a.signal_type === "Production collapse").length,
    watchlistHits: alerts.filter((a) => a.signal_type.toLowerCase().includes("watchlist")).length,
  };

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-3xl font-semibold">Texas Distress Signal Dashboard</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-400">
          Prioritize distressed energy assets and operators by combining production anomalies, bankruptcy events, and sale-process docket signals.
        </p>
      </section>

      <KpiRow kpis={kpis} />

      <section className="grid gap-6 xl:grid-cols-[2fr_1fr]">
        <div>
          <SectionTitle title="Alert feed" subtitle="Newest actionable events across monitored Texas assets and operators." />
          <div className="mt-4">
            <AlertFeed alerts={alerts} />
          </div>
        </div>
        <RightRail watchlists={watchlists} />
      </section>
    </div>
  );
}
