"use client";
export default function ErrorBoundary({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <section role="alert">
      <p className="eyebrow">UNAVAILABLE</p>
      <h1>This page couldn’t load</h1>
      <p>Please try again.</p>
      <button className="button" onClick={reset}>
        Try again
      </button>
    </section>
  );
}
