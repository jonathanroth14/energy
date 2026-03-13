import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Alert } from "@/lib/types";
import { formatDate } from "@/lib/utils";

function severityTone(severity: string): "red" | "amber" | "slate" {
  if (severity.toLowerCase() === "high") return "red";
  if (severity.toLowerCase() === "medium") return "amber";
  return "slate";
}

export function AlertCard({ alert }: { alert: Alert }) {
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900 p-5 shadow-sm">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="cyan">{alert.signal_type}</Badge>
        <Badge tone={severityTone(alert.severity)}>{alert.severity}</Badge>
      </div>

      <h3 className="mt-3 text-base font-semibold text-slate-100">{alert.title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-300">{alert.why_fired}</p>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800 pt-3 text-xs text-slate-400">
        <span>{formatDate(alert.event_date)}</span>
        <div className="flex items-center gap-4">
          <a href={alert.source_url} target="_blank" rel="noreferrer" className="text-cyan-400 hover:text-cyan-300">
            Source
          </a>
          {alert.asset_id ? (
            <Link href={`/assets/${alert.asset_id}`} className="text-slate-200 hover:text-white">
              View asset
            </Link>
          ) : (
            <Link href={`/alerts/${alert.id}`} className="text-slate-200 hover:text-white">
              View case
            </Link>
          )}
        </div>
      </div>
    </article>
  );
}
