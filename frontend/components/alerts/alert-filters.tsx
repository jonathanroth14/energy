"use client";

import { useMemo, useState } from "react";

import { Alert } from "@/lib/types";

type Props = {
  alerts: Alert[];
  onChange: (alerts: Alert[]) => void;
};

export function AlertFilters({ alerts, onChange }: Props) {
  const [severity, setSeverity] = useState("all");
  const [signalType, setSignalType] = useState("all");

  const signalOptions = useMemo(() => {
    return ["all", ...Array.from(new Set(alerts.map((a) => a.signal_type)))];
  }, [alerts]);

  function applyFilters(nextSeverity: string, nextSignalType: string) {
    const filtered = alerts.filter((a) => {
      const severityOk = nextSeverity === "all" || a.severity === nextSeverity;
      const signalOk = nextSignalType === "all" || a.signal_type === nextSignalType;
      return severityOk && signalOk;
    });
    onChange(filtered);
  }

  return (
    <div className="grid gap-3 rounded-xl border border-slate-800 bg-slate-900 p-4 md:grid-cols-2">
      <label className="text-sm text-slate-300">
        Severity
        <select
          className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2"
          value={severity}
          onChange={(e) => {
            const value = e.target.value;
            setSeverity(value);
            applyFilters(value, signalType);
          }}
        >
          <option value="all">All</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </label>

      <label className="text-sm text-slate-300">
        Signal type
        <select
          className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2"
          value={signalType}
          onChange={(e) => {
            const value = e.target.value;
            setSignalType(value);
            applyFilters(severity, value);
          }}
        >
          {signalOptions.map((signal) => (
            <option key={signal} value={signal}>
              {signal === "all" ? "All" : signal}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
