import { mockAlerts, mockAssetDetails, mockAssets, mockWatchlists } from "@/lib/mock-data";
import { Alert, Asset, AssetDetail, Watchlist } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function tryFetch<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getAlerts(): Promise<Alert[]> {
  const live = await tryFetch<Alert[]>("/alerts");
  return live && live.length > 0 ? live : mockAlerts;
}

export async function getAlert(id: string): Promise<Alert | null> {
  const live = await tryFetch<Alert>(`/alerts/${id}`);
  if (live) return live;
  return mockAlerts.find((a) => a.id === Number(id)) ?? null;
}

export async function getAssets(): Promise<Asset[]> {
  const live = await tryFetch<Asset[]>("/assets");
  return live && live.length > 0 ? live : mockAssets;
}

export async function getAsset(id: string): Promise<AssetDetail | null> {
  const live = await tryFetch<AssetDetail>(`/assets/${id}`);
  if (live) return live;
  return mockAssetDetails[Number(id)] ?? null;
}

export async function getWatchlists(): Promise<Watchlist[]> {
  const live = await tryFetch<Watchlist[]>("/watchlists");
  return live && live.length > 0 ? live : mockWatchlists;
}
