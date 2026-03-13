import { ProductionRecord } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export function ProductionTrend({ records }: { records: ProductionRecord[] }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900">
      <div className="border-b border-slate-800 px-4 py-3 text-sm font-medium text-slate-200">Production trend</div>
      <div className="divide-y divide-slate-800">
        {records.map((record) => (
          <div key={record.period_date} className="grid grid-cols-2 gap-2 px-4 py-3 text-sm md:grid-cols-4">
            <span className="text-slate-400">{formatDate(record.period_date)}</span>
            <span>{record.oil_bbl.toFixed(0)} bbl oil</span>
            <span>{record.gas_mcf.toFixed(0)} mcf gas</span>
            <span className="text-slate-400">{record.water_bbl.toFixed(0)} bbl water</span>
          </div>
        ))}
      </div>
    </div>
  );
}
