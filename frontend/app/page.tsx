import Link from "next/link";
import { AlertCard } from "@/components/alert-card";
import { getAlerts, getAssets } from "@/lib/api";

export default async function DashboardPage() {
  const [alerts, assets] = await Promise.all([getAlerts(), getAssets()]);

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-bold">Texas Distress Signal Feed</h1>
        <p className="mt-1 text-slate-400">Actionable alerts on production, inactivity, bankruptcy, and sale-process signals.</p>
      </section>

      <section className="grid gap-3 md:grid-cols-2">
        {alerts.map((alert) => (
          <AlertCard key={alert.id} alert={alert} />
        ))}
      </section>

      <section>
        <h2 className="mb-3 text-xl font-semibold">Assets</h2>
        <div className="grid gap-2 md:grid-cols-3">
          {assets.map((asset) => (
            <Link key={asset.id} href={`/assets/${asset.id}`} className="rounded border border-slate-800 p-3 hover:border-cyan-500">
              <div className="font-medium">{asset.name}</div>
              <div className="text-xs text-slate-400">{asset.county} • {asset.field}</div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
