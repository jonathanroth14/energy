export type Alert = {
  id: number;
  asset_id: number | null;
  signal_type: string;
  severity: string;
  title: string;
  why_fired: string;
  event_date: string;
  source_url: string;
};

export type Asset = {
  id: number;
  operator_id: number;
  name: string;
  county: string;
  field: string;
  basin: string;
  status: string;
};

export type AssetDetail = Asset & {
  production_records: { period_date: string; oil_bbl: number; gas_mcf: number; water_bbl: number }[];
  alerts: Alert[];
};

export type Watchlist = {
  id: number;
  name: string;
  description: string | null;
  items: { id: number; asset_id: number; notes: string | null }[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed request ${path}`);
  return res.json();
}

export const getAlerts = () => fetchJson<Alert[]>("/alerts");
export const getAssets = () => fetchJson<Asset[]>("/assets");
export const getAsset = (id: string) => fetchJson<AssetDetail>(`/assets/${id}`);
export const getWatchlists = () => fetchJson<Watchlist[]>("/watchlists");
