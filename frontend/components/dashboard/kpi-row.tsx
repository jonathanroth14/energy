import { KpiCard } from "@/components/ui/kpi-card";
import { DashboardKpis } from "@/lib/types";

export function KpiRow({ kpis }: { kpis: DashboardKpis }) {
  return (
    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard label="New Alerts" value={kpis.newAlerts} />
      <KpiCard label="Bankruptcy Cases" value={kpis.bankruptcyCases} />
      <KpiCard label="Production Collapses" value={kpis.productionCollapses} />
      <KpiCard label="Watchlist Hits" value={kpis.watchlistHits} />
    </section>
  );
}
