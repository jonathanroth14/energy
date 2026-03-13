import "./globals.css";
import Link from "next/link";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-800 bg-slate-900/80">
          <nav className="mx-auto flex max-w-6xl gap-6 p-4 text-sm">
            <Link href="/" className="font-semibold">Frontier Radar</Link>
            <Link href="/watchlists">Watchlists</Link>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl p-6">{children}</main>
      </body>
    </html>
  );
}
