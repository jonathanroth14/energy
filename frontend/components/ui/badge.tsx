import { cx } from "@/lib/utils";

export function Badge({
  children,
  tone = "slate",
}: {
  children: React.ReactNode;
  tone?: "slate" | "red" | "amber" | "cyan" | "violet";
}) {
  const styles: Record<string, string> = {
    slate: "bg-slate-800 text-slate-200 border-slate-700",
    red: "bg-red-500/15 text-red-300 border-red-500/30",
    amber: "bg-amber-500/15 text-amber-300 border-amber-500/30",
    cyan: "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
    violet: "bg-violet-500/15 text-violet-300 border-violet-500/30",
  };

  return <span className={cx("rounded-md border px-2 py-1 text-xs font-medium", styles[tone])}>{children}</span>;
}
