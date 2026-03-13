import { getAsset } from "@/lib/api";

export default async function AssetDetailPage({ params }: { params: { id: string } }) {
  const asset = await getAsset(params.id);

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-2xl font-bold">{asset.name}</h1>
        <p className="text-slate-400">{asset.county} County • {asset.field} • {asset.basin}</p>
      </section>

      <section>
        <h2 className="mb-2 text-lg font-semibold">Production History</h2>
        <div className="rounded border border-slate-800">
          {asset.production_records.map((record) => (
            <div key={record.period_date} className="flex justify-between border-b border-slate-800 p-3 text-sm last:border-none">
              <span>{record.period_date}</span>
              <span>{record.oil_bbl.toFixed(0)} bbl oil / {record.gas_mcf.toFixed(0)} mcf gas</span>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-2 text-lg font-semibold">Related Alerts</h2>
        <div className="space-y-2">
          {asset.alerts.map((a) => (
            <div key={a.id} className="rounded border border-slate-800 p-3 text-sm">
              <div className="font-medium">{a.title}</div>
              <a className="text-cyan-400" href={a.source_url} target="_blank">Source</a>
            </div>
          ))}
        </div>
      </section>

      <button className="rounded bg-cyan-600 px-4 py-2 text-sm font-semibold hover:bg-cyan-500">Add to Watchlist</button>
    </div>
  );
}
