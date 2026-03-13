import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { SectionTitle } from "@/components/ui/section-title";
import { Watchlist } from "@/lib/types";

export function RightRail({ watchlists }: { watchlists: Watchlist[] }) {
  return (
    <aside className="space-y-4">
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <SectionTitle title="Saved watchlists" subtitle="Quick access to priority pools." />
        <div className="mt-3 space-y-2">
          {watchlists.length === 0 ? (
            <p className="text-sm text-slate-500">No watchlists yet. Create one from the watchlists page.</p>
          ) : (
            watchlists.map((watchlist) => (
              <Link
                key={watchlist.id}
                href="/watchlists"
                className="flex items-center justify-between rounded-md border border-slate-800 px-3 py-2 text-sm hover:border-cyan-700"
              >
                <span className="text-slate-200">{watchlist.name}</span>
                <Badge tone="violet">{watchlist.items.length}</Badge>
              </Link>
            ))
          )}
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <SectionTitle title="Quick filters" subtitle="Common triage views." />
        <div className="mt-3 grid gap-2 text-sm text-slate-300">
          {[
            "High severity only",
            "Bankruptcy activity",
            "Permian county focus",
            "Sale process keywords",
          ].map((label) => (
            <button key={label} className="rounded-md border border-slate-700 px-3 py-2 text-left hover:border-cyan-700">
              {label}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
