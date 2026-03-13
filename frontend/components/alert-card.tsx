import { Alert } from "@/lib/api";

export function AlertCard({ alert }: { alert: Alert }) {
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900 p-4 shadow">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-semibold">{alert.title}</h3>
        <span className="rounded bg-amber-500/20 px-2 py-1 text-xs uppercase text-amber-300">{alert.severity}</span>
      </div>
      <p className="text-sm text-slate-300">{alert.why_fired}</p>
      <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
        <span>{alert.signal_type} • {alert.event_date}</span>
        <a href={alert.source_url} className="text-cyan-400 hover:underline" target="_blank">Source</a>
      </div>
    </article>
  );
}
