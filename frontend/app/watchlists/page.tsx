import { getWatchlists } from "@/lib/api";

export default async function WatchlistsPage() {
  const watchlists = await getWatchlists();

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">Watchlists</h1>
      <div className="space-y-4">
        {watchlists.map((watchlist) => (
          <div key={watchlist.id} className="rounded border border-slate-800 p-4">
            <h2 className="font-semibold">{watchlist.name}</h2>
            <p className="text-sm text-slate-400">{watchlist.description}</p>
            <p className="mt-2 text-xs text-slate-500">{watchlist.items.length} tracked assets</p>
          </div>
        ))}
      </div>
    </div>
  );
}
