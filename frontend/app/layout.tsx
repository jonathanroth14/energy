import "./globals.css";
import Link from "next/link";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <header className="sticky top-0 z-20 border-b border-slate-800 bg-slate-950/90 backdrop-blur">
          <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <Link href="/" className="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-300">
              Frontier Radar
            </Link>
            <div className="flex gap-6 text-sm text-slate-300">
              <Link href="/" className="hover:text-white">Dashboard</Link>
              <Link href="/watchlists" className="hover:text-white">Watchlists</Link>
            </div>
          </nav>
          <div className="border-t border-slate-800 bg-amber-500/10 px-6 py-2 text-xs text-amber-200">
            Demo Mode: using seeded/sample data for product walkthroughs.
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
