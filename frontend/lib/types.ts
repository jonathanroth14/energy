export type Severity = "low" | "medium" | "high";

export type AlertType =
  | "Production collapse"
  | "Inactivity / shut-in proxy"
  | "New bankruptcy filing"
  | "Asset sale motion keyword hit";

export type Alert = {
  id: number;
  asset_id: number | null;
  court_case_id?: number | null;
  signal_type: AlertType | string;
  severity: Severity | string;
  title: string;
  why_fired: string;
  event_date: string;
  source_url: string;
};

export type ProductionRecord = {
  period_date: string;
  oil_bbl: number;
  gas_mcf: number;
  water_bbl: number;
};

export type Asset = {
  id: number;
  operator_id: number;
  name: string;
  county: string;
  field: string;
  basin: string;
  status: string;
  operator_name?: string;
};

export type AssetDetail = Asset & {
  production_records: ProductionRecord[];
  alerts: Alert[];
};

export type WatchlistItem = {
  id: number;
  asset_id: number;
  notes: string | null;
};

export type Watchlist = {
  id: number;
  name: string;
  description: string | null;
  items: WatchlistItem[];
};

export type DashboardKpis = {
  newAlerts: number;
  bankruptcyCases: number;
  productionCollapses: number;
  watchlistHits: number;
};
