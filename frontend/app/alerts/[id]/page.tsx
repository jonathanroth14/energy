import Link from "next/link";
import { notFound } from "next/navigation";

import { AlertCard } from "@/components/alerts/alert-card";
import { SectionTitle } from "@/components/ui/section-title";
import { getAlert } from "@/lib/api";

export default async function AlertDetailPage({ params }: { params: { id: string } }) {
  const alert = await getAlert(params.id);
  if (!alert) notFound();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <SectionTitle title="Alert detail" subtitle="Traceable context for immediate evaluation." />
        <Link href="/" className="text-sm text-cyan-400 hover:text-cyan-300">
          Back to dashboard
        </Link>
      </div>

      <AlertCard alert={alert} />

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-5">
        <h2 className="text-base font-semibold">Linked record</h2>
        <p className="mt-2 text-sm text-slate-400">
          {alert.asset_id
            ? `This alert is tied to Asset #${alert.asset_id}.`
            : `This alert is tied to Case #${alert.court_case_id ?? "n/a"}.`}
        </p>
      </section>
    </div>
  );
}
