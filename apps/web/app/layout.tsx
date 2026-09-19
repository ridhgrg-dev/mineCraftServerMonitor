import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "MineOps · Server operations",
  description: "A foundation for reliable game server operations.",
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        <header>
          <div className="header-inner">
            <Link className="brand" href="/">
              MineOps<span>SERVER OPERATIONS</span>
            </Link>
            <nav aria-label="Main navigation">
              <Link href="/">Workspace</Link>
              <Link href="/system">System health</Link>
            </nav>
            <span className="phase">Foundation</span>
          </div>
        </header>
        <main id="main" tabIndex={-1}>
          {children}
        </main>
        <footer>
          MineOps <span>Infrastructure foundation · v0.1.0</span>
        </footer>
      </body>
    </html>
  );
}
