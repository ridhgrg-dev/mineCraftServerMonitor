import { cpSync } from "node:fs";
import { spawn } from "node:child_process";
// Next standalone output omits static assets; include them for native smoke tests.
cpSync(".next/static", ".next/standalone/apps/web/.next/static", {
  recursive: true,
});
const child = spawn(process.execPath, [".next/standalone/apps/web/server.js"], {
  stdio: "inherit",
  env: { ...process.env, HOSTNAME: process.env.HOSTNAME ?? "127.0.0.1" },
});
for (const signal of ["SIGINT", "SIGTERM"])
  process.on(signal, () => child.kill(signal));
child.on("exit", (code) => process.exit(code ?? 1));
