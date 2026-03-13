import { Alert, Asset, AssetDetail, Watchlist } from "@/lib/types";

const operators = [
  "Lone Star Operating",
  "Permian Ridge Energy",
  "Bluebonnet Production",
  "Rio Grande Petroleum",
  "South Plains Exploration",
];

export const mockAssets: Asset[] = Array.from({ length: 10 }).map((_, i) => ({
  id: i + 1,
  operator_id: (i % operators.length) + 1,
  operator_name: operators[i % operators.length],
  name: `${["Mustang", "Falcon", "Coyote", "Pioneer", "Mesa"][i % 5]} Unit ${i + 1}`,
  county: ["Midland", "Reeves", "Howard", "Karnes", "La Salle"][i % 5],
  field: ["Spraberry", "Wolfcamp", "Bone Spring", "Eagle Ford", "Yates"][i % 5],
  basin: i % 2 === 0 ? "Permian" : "Eagle Ford",
  status: i % 3 === 0 ? "watch" : "active",
}));

export const mockAlerts: Alert[] = Array.from({ length: 16 }).map((_, i) => {
  const signalTypes = [
    "Production collapse",
    "Inactivity / shut-in proxy",
    "New bankruptcy filing",
    "Asset sale motion keyword hit",
  ];
  const severity = ["high", "medium", "low"][i % 3];
  return {
    id: i + 1,
    asset_id: i % 4 === 2 ? null : ((i % mockAssets.length) + 1),
    court_case_id: i % 4 === 2 ? (i % 5) + 1 : null,
    signal_type: signalTypes[i % signalTypes.length],
    severity,
    title: `${signalTypes[i % signalTypes.length]} – ${mockAssets[i % mockAssets.length].county}`,
    why_fired:
      i % 4 === 0
        ? "Latest full month production declined more than 40% versus trailing 3-month average."
        : i % 4 === 1
          ? "Asset has no reported production for two consecutive periods after prior activity."
          : i % 4 === 2
            ? "New Chapter filing detected for Texas energy-related debtor in public court records."
            : "Docket entry contains deal-process keywords such as 363, APA, stalking horse, or bid procedures.",
    event_date: `2026-03-${String((i % 28) + 1).padStart(2, "0")}`,
    source_url: `https://example.com/source/${i + 1}`,
  };
});

export const mockAssetDetails: Record<number, AssetDetail> = Object.fromEntries(
  mockAssets.map((asset) => [
    asset.id,
    {
      ...asset,
      production_records: [0, 1, 2, 3, 4, 5].map((monthOffset) => ({
        period_date: `2025-${String(12 - monthOffset).padStart(2, "0")}-01`,
        oil_bbl: Math.max(120, 820 - monthOffset * 100 - asset.id * 8),
        gas_mcf: Math.max(500, 3500 - monthOffset * 220 - asset.id * 15),
        water_bbl: 200 + monthOffset * 30 + asset.id,
      })),
      alerts: mockAlerts.filter((a) => a.asset_id === asset.id).slice(0, 4),
    },
  ]),
);

export const mockWatchlists: Watchlist[] = [
  {
    id: 1,
    name: "Permian Distress",
    description: "Higher-conviction opportunities in Midland/Reeves with recent collapse signals.",
    items: [
      { id: 1, asset_id: 1, notes: "Potential PDP underwrite" },
      { id: 2, asset_id: 3, notes: "Monitor lender actions" },
    ],
  },
  {
    id: 2,
    name: "Bankruptcy Tracker",
    description: "Court-driven transaction opportunities in active TX Chapter 11 dockets.",
    items: [{ id: 3, asset_id: 2, notes: "Track sale motion timing" }],
  },
];
