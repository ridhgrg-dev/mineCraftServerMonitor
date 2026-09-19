import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
const paths = [
  "packages/api-client/openapi.json",
  "packages/api-client/src/schema.d.ts",
];
const before = paths.map((path) => readFileSync(path, "utf8"));
execFileSync("pnpm", ["api:generate"], { stdio: "inherit" });
if (paths.some((path, index) => readFileSync(path, "utf8") !== before[index])) {
  throw new Error(
    "Generated API client drift: regenerate and commit the contracts.",
  );
}
