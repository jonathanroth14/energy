"use client";

import { useState } from "react";

import { AlertCard } from "@/components/alerts/alert-card";
import { AlertFilters } from "@/components/alerts/alert-filters";
import { EmptyState } from "@/components/ui/empty-state";
import { Alert } from "@/lib/types";

export function AlertFeed({ alerts }: { alerts: Alert[] }) {
  const [visibleAlerts, setVisibleAlerts] = useState(alerts);

  return (
    <div className="space-y-4">
      <AlertFilters alerts={alerts} onChange={setVisibleAlerts} />
      {visibleAlerts.length === 0 ? (
        <EmptyState title="No alerts for active filters" body="Adjust filter controls to broaden the feed." />
      ) : (
        <div className="space-y-3">
          {visibleAlerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      )}
    </div>
  );
}
