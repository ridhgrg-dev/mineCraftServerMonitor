import { createApiClient } from "@platform/api-client";
export const dynamic = "force-dynamic";

export default async function SystemPage() {
  let reachable = false;
  let ready = false;
  const baseUrl = process.env.API_INTERNAL_URL;
  if (baseUrl) {
    const client = createApiClient(baseUrl);
    const results = await Promise.allSettled([
      client.GET("/health/live", {
        signal: AbortSignal.timeout(3000),
        cache: "no-store",
      }),
      client.GET("/health/ready", {
        signal: AbortSignal.timeout(3000),
        cache: "no-store",
      }),
    ]);
    reachable =
      results[0].status === "fulfilled" &&
      results[0].value.data?.status === "ok";
    ready =
      results[1].status === "fulfilled" &&
      results[1].value.data?.status === "ok";
  }
  return (
    <>
      <p className="eyebrow">SYSTEM</p>
      <h1>Application health</h1>
      <p className="intro">
        Live checks of the control plane and its required dependencies.
      </p>
      <dl className="health-list">
        <div>
          <dt>API process</dt>
          <dd>{reachable ? "Responding" : "Unavailable"}</dd>
        </div>
        <div>
          <dt>Required dependencies</dt>
          <dd>{ready ? "Ready" : "Not ready"}</dd>
        </div>
      </dl>
      <p className="muted">
        {baseUrl
          ? "Refresh this page to run the checks again."
          : "The API connection has not been configured for this web process."}
      </p>
    </>
  );
}
