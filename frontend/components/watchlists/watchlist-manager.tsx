"use client";

import { useMemo, useState } from "react";

import { EmptyState } from "@/components/ui/empty-state";
import { Alert, Asset, Watchlist } from "@/lib/types";

type Props = {
  initialWatchlists: Watchlist[];
  assets: Asset[];
  alerts: Alert[];
};

export function WatchlistManager({ initialWatchlists, assets, alerts }: Props) {
  const [watchlists, setWatchlists] = useState(initialWatchlists);
  const [name, setName] = useState("");

  const firstWatchlistId = watchlists[0]?.id;

  const watchlistHitAlerts = useMemo(() => {
    const trackedAssetIds = new Set(watchlists.flatMap((w) => w.items.map((item) => item.asset_id)));
    return alerts.filter((alert) => (alert.asset_id ? trackedAssetIds.has(alert.asset_id) : false)).slice(0, 8);
  }, [watchlists, alerts]);

  function addWatchlist() {
    if (!name.trim()) return;
    const next: Watchlist = {
      id: Date.now(),
      name: name.trim(),
      description: "Created locally in demo mode.",
      items: [],
    };
    setWatchlists((prev) => [next, ...prev]);
    setName("");
  }

  function addTrackedItem(assetId: number) {
    if (!firstWatchlistId) return;
    setWatchlists((prev) =>
      prev.map((watchlist) => {
        if (watchlist.id !== firstWatchlistId) return watchlist;
        if (watchlist.items.some((item) => item.asset_id === assetId)) return watchlist;
        return {
          ...watchlist,
          items: [...watchlist.items, { id: Date.now(), asset_id: assetId, notes: "Added from UI" }],
        };
      }),
    );
  }

  function removeTrackedItem(watchlistId: number, itemId: number) {
    setWatchlists((prev) =>
      prev.map((watchlist) => {
        if (watchlist.id !== watchlistId) return watchlist;
        return { ...watchlist, items: watchlist.items.filter((item) => item.id !== itemId) };
      }),
    );
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[2fr_1fr]">
      <div className="space-y-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <h2 className="text-lg font-semibold">Watchlists</h2>
          <div className="mt-3 flex gap-2">
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              placeholder="Add new watchlist"
            />
            <button onClick={addWatchlist} className="rounded-md bg-cyan-600 px-4 py-2 text-sm font-semibold hover:bg-cyan-500">
              Add
            </button>
          </div>
        </div>

        {watchlists.map((watchlist) => (
          <div key={watchlist.id} className="rounded-xl border border-slate-800 bg-slate-900 p-4">
            <h3 className="text-base font-semibold">{watchlist.name}</h3>
            <p className="mt-1 text-sm text-slate-400">{watchlist.description}</p>
            <div className="mt-3 space-y-2">
              {watchlist.items.length === 0 ? (
                <p className="text-sm text-slate-500">No tracked assets yet.</p>
              ) : (
                watchlist.items.map((item) => {
                  const asset = assets.find((a) => a.id === item.asset_id);
                  return (
                    <div key={item.id} className="flex items-center justify-between rounded-md border border-slate-800 px-3 py-2 text-sm">
                      <span>{asset?.name ?? `Asset #${item.asset_id}`}</span>
                      <button
                        className="text-red-300 hover:text-red-200"
                        onClick={() => removeTrackedItem(watchlist.id, item.id)}
                      >
                        Remove
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <h2 className="text-lg font-semibold">Add tracked items</h2>
          <div className="mt-3 space-y-2">
            {assets.slice(0, 8).map((asset) => (
              <button
                key={asset.id}
                className="w-full rounded-md border border-slate-800 px-3 py-2 text-left text-sm hover:border-cyan-700"
                onClick={() => addTrackedItem(asset.id)}
              >
                {asset.name}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <h2 className="text-lg font-semibold">Recent watchlist-triggered alerts</h2>
          {watchlistHitAlerts.length === 0 ? (
            <div className="mt-3">
              <EmptyState title="No watchlist hits" body="Track assets to see alert hits here." />
            </div>
          ) : (
            <div className="mt-3 space-y-2">
              {watchlistHitAlerts.map((alert) => (
                <div key={alert.id} className="rounded-md border border-slate-800 px-3 py-2 text-sm">
                  <div className="font-medium text-slate-200">{alert.title}</div>
                  <div className="text-xs text-slate-400">{alert.event_date}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
