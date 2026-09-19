import Link from "next/link";
export default function NotFound() {
  return (
    <>
      <p className="eyebrow">404</p>
      <h1>Page not found</h1>
      <p>This address doesn’t point to a page in the workspace.</p>
      <Link className="button" href="/">
        Return to workspace
      </Link>
    </>
  );
}
