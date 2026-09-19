import Link from "next/link";
export default function Home() {
  return (
    <>
      <p className="eyebrow">WORKSPACE</p>
      <h1>
        Server operations,
        <br />
        with a clear view.
      </h1>
      <p className="intro">
        A dedicated place to understand and manage your game servers.
      </p>
      <section className="empty-panel" aria-labelledby="foundation-title">
        <div className="server-symbol" aria-hidden="true">
          ▤
        </div>
        <div>
          <p className="eyebrow">GETTING STARTED</p>
          <h2 id="foundation-title">Your workspace starts here</h2>
          <p>
            The application foundation is ready to explore. Accounts,
            organizations and server connections will arrive in later
            development phases.
          </p>
          <Link className="button" href="/system">
            Check system health <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>
      <section className="principles" aria-label="Platform principles">
        <div>
          <h2>Private by design</h2>
          <p>
            Server connections will originate from your host, keeping local
            control interfaces private.
          </p>
        </div>
        <div>
          <h2>Clear operational state</h2>
          <p>
            Future controls will report observed results and keep a history of
            requested actions.
          </p>
        </div>
        <div>
          <h2>Built around your servers</h2>
          <p>
            A separate host agent and game integration keep responsibilities
            focused.
          </p>
        </div>
      </section>
    </>
  );
}
