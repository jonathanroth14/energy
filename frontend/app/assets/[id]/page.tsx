import Link from "next/link";
import { notFound } from "next/navigation";

import { AlertCard } from "@/components/alerts/alert-card";
import { AddToWatchlistButton } from "@/components/assets/add-to-watchlist-button";
import { ProductionTrend } from "@/components/assets/production-trend";
import { EmptyState } from "@/components/ui/empty-state";
import { getAsset } from "@/lib/api";

export default async function AssetDetailPage({ params }: { params: { id: string } }) {
  const asset = await getAsset(params.id);
  if (!asset) notFound();

  return (
    <div className="space-y-6">
      <header className="rounded-xl border border-slate-800 bg-slate-900 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold">{asset.name}</h1>
            <p className="mt-2 text-sm text-slate-400">
              Operator: {asset.operator_name ?? `Operator #${asset.operator_id}`} • County: {asset.county} • Field: {asset.field}
            </p>
          </div>
          <AddToWatchlistButton assetName={asset.name} />
        </div>
      </header>

      <ProductionTrend records={asset.production_records} />

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Related alerts</h2>
          <Link href="/" className="text-sm text-cyan-400 hover:text-cyan-300">View all alerts</Link>
        </div>
        {asset.alerts.length === 0 ? (
          <EmptyState title="No related alerts" body="This asset has no matching events in the current window." />
        ) : (
          <div className="space-y-3">
            {asset.alerts.map((alert) => (
              <AlertCard key={alert.id} alert={alert} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
