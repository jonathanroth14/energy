"use client";

import { useState } from "react";

export function AddToWatchlistButton({ assetName }: { assetName: string }) {
  const [added, setAdded] = useState(false);

  return (
    <button
      onClick={() => setAdded(true)}
      className="rounded-md bg-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-500"
    >
      {added ? `${assetName} saved to watchlist` : "Add to watchlist"}
    </button>
  );
}
