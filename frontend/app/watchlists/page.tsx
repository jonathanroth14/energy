import { WatchlistManager } from "@/components/watchlists/watchlist-manager";
import { SectionTitle } from "@/components/ui/section-title";
import { getAlerts, getAssets, getWatchlists } from "@/lib/api";

export default async function WatchlistsPage() {
  const [watchlists, assets, alerts] = await Promise.all([getWatchlists(), getAssets(), getAlerts()]);

  return (
    <div className="space-y-6">
      <SectionTitle
        title="Watchlists"
        subtitle="Track priority assets, maintain investor focus lists, and monitor watchlist-triggered alerts."
      />
      <WatchlistManager initialWatchlists={watchlists} assets={assets} alerts={alerts} />
    </div>
  );
}
