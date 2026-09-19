# Locked dependencies and compatibility

Resolved against official documentation and package registries on 2026-09-18. Exact direct dependencies are in manifests; full transitive versions/hashes are in `pnpm-lock.yaml`, `apps/api/uv.lock`, Gradle lockfiles and Gradle verification metadata. The Go harness uses only the standard library and needs no `go.sum`.

## Toolchains and containers

| Component                     | Selected version                       | Reason/evidence                                                                                              |
| ----------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Node                          | 24.21.0                                | Installed LTS runtime; Next build and tests validated                                                        |
| pnpm                          | 12.4.2                                 | Exact workspace package-manager version and strict peer checks                                               |
| Python                        | 3.14.7 container/CI; 3.14.4 native Mac | Same supported minor; native wheel install and wheel/sdist build passed                                      |
| uv                            | 0.12.16                                | Exact lock/sync tool and API image build tool                                                                |
| Go                            | 1.27.1                                 | Official checksum-verified toolchain; Darwin amd64/Linux amd64/arm64 builds                                  |
| Java                          | Temurin 25.0.4.1+1                     | Official checksum-verified Intel Mac JDK; Paper 26.2 requirement; CI uses Adoptium SemVer `25.0.4+101.0.LTS` |
| Gradle                        | 9.7.1                                  | Wrapper distribution and wrapper JAR SHA-256 verified                                                        |
| Paper API                     | 26.2.build.124-stable                  | Exact published stable coordinate; no dynamic/snapshot dependency                                            |
| JUnit                         | 6.0.3                                  | Locked test dependency, runs on Java 25                                                                      |
| Spotless / google-java-format | 8.6.0 / 1.35.0                         | Pinned Java formatting; compiler uses all lint warnings as errors                                            |
| PostgreSQL                    | 18.6-trixie                            | Supported relational baseline and role/RLS preparation                                                       |
| Redis server                  | 8.10.1-alpine                          | Newest published official container observed; 8.10.2 source release has no matching official image yet       |
| Caddy                         | 2.11.4-alpine                          | Stable official release with production TLS edge configuration                                               |
| Compose                       | 5.5.1 tested                           | Standalone CLI and Colima integration; Docker Engine 29.5.2 under Colima                                     |
| Buildx                        | 0.37.1 tested                          | Locally downloaded checksum-verified plugin; required for modern Dockerfiles                                 |

Base Python/Node/PostgreSQL/Redis/Caddy images pin immutable multi-platform index digests recorded in [image manifests](../infrastructure/docker/image-manifests.json). Docker Hub manifests were checked for both Linux amd64 and arm64. An index existing is not proof of a successful application image build; consult [results](phase-1-results.md).

## Direct package versions

| Package                   | Exact version   | Scope           |
| ------------------------- | --------------- | --------------- |
| prettier                  | 3.9.7           | devDependencies |
| openapi-typescript        | 7.13.0          | devDependencies |
| @playwright/test          | 1.63.0          | devDependencies |
| next                      | 16.3.5          | dependencies    |
| react                     | 19.3.0          | dependencies    |
| react-dom                 | 19.3.0          | dependencies    |
| typescript                | 6.0.3           | devDependencies |
| @types/node               | 24.13.5         | devDependencies |
| @types/react              | 19.3.0          | devDependencies |
| @types/react-dom          | 19.3.0          | devDependencies |
| tailwindcss               | 4.3.3           | devDependencies |
| @tailwindcss/postcss      | 4.3.3           | devDependencies |
| eslint                    | 9.39.5          | devDependencies |
| eslint-config-next        | 16.3.5          | devDependencies |
| vitest                    | 5.0.1           | devDependencies |
| @testing-library/react    | 16.3.3          | devDependencies |
| @testing-library/jest-dom | 7.0.1           | devDependencies |
| jsdom                     | 30.1.0          | devDependencies |
| openapi-fetch             | 0.17.0          | dependencies    |
| fastapi                   | 0.141.1         | Python          |
| uvicorn                   | 0.53.0          | Python          |
| pydantic-settings         | 2.15.0          | Python          |
| sqlalchemy[asyncio]       | 2.0.54          | Python          |
| alembic                   | 1.20.0          | Python          |
| psycopg[binary]           | 3.3.6           | Python          |
| redis                     | 8.1.0           | Python          |
| pytest                    | 9.1.1           | Python          |
| pytest-asyncio            | 1.4.0           | Python          |
| httpx                     | 0.28.1          | Python          |
| ruff                      | 0.16.8          | Python          |
| mypy                      | 2.3.1           | Python          |
| jsonschema                | 4.26.0          | Python          |
| types-jsonschema          | 4.26.0.20260518 | Python          |
| pyyaml                    | 6.0.3           | Python          |
| types-pyyaml              | 6.0.12.20260906 | Python          |
| pip-audit                 | 2.10.1          | Python          |

## Compatibility decisions

Next 16.3.5 accepts React 19.3.0. ESLint 10 and TypeScript 7 were rejected during initial resolution because current Next lint plugins require ESLint 9 and TypeScript below 6.1. Selected ESLint 9.39.5 and TypeScript 6.0.3 pass strict peer resolution and application checks. ESLint 9 emits a deprecation notice; upgrade only when Next plugin peers support the replacement. `next build --webpack` avoids the observed Turbopack worker port-binding restriction on this Mac; both builders are supported by Next.

Current Playwright 1.63.0 bundled Chromium no longer supports this Mac's macOS 13.7.8. Local smoke tests use the installed Chrome channel; Linux CI installs Playwright's pinned Chromium. This keeps current tooling without silently downgrading the browser dependency. Docker development on older macOS may require Colima or a supported Linux host.

Psycopg binary, Pydantic core, SQLAlchemy and greenlet locked distributions contain CPython 3.14-compatible x86_64/aarch64 Linux wheels. Native Intel macOS dependency installation succeeded. Container builds independently exercise the Linux interpreter; ARM Go cross-compilation is separate from ARM container runtime testing.

## Significant dependency purpose and license inventory

| Dependency family                        | Purpose                                    | Upstream license family                                                     |
| ---------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------- |
| Next, React, Tailwind, FastAPI, Pydantic | UI, HTTP routing, validation/settings      | MIT                                                                         |
| SQLAlchemy, Alembic                      | Relational transactions and migrations     | MIT                                                                         |
| Uvicorn                                  | ASGI process server                        | BSD-3-Clause                                                                |
| Psycopg                                  | PostgreSQL driver                          | LGPL-3.0-or-later; preserve bundled-library notices                         |
| redis-py                                 | Optional cache client                      | MIT                                                                         |
| Redis server                             | Ephemeral coordination, separate service   | Redis 8 offers AGPLv3/SSPLv1/RSALv2; this foundation uses the AGPLv3 option |
| PostgreSQL                               | Sole durable database                      | PostgreSQL License                                                          |
| Go                                       | Agent compiler/standard library            | BSD-3-Clause                                                                |
| Paper API                                | Compile-only public server API             | GPL-3.0; API is not bundled in the plugin JAR                               |
| Temurin/OpenJDK                          | Java compiler/runtime                      | GPL-2.0 with Classpath Exception                                            |
| Gradle, Caddy, TypeScript, Playwright    | Build, edge proxy, types and browser tests | Apache-2.0                                                                  |
| pytest, Ruff, mypy, Vitest               | Tests/lint/types                           | MIT                                                                         |

Retain exact upstream license notices when distributing dependencies/images; transitive licenses still apply. This inventory is not a claim that a full commercial distribution audit has been completed. Redis is unmodified and isolated from the application; license obligations must remain in release packaging. No extra queue framework, crypto implementation, host-metrics library or generic process executor is introduced in Phase 1.

## Official sources

- [Next installation and requirements](https://nextjs.org/docs/app/getting-started/installation), [React releases](https://react.dev/versions), [Node support schedule](https://nodejs.org/en/about/previous-releases)
- [TypeScript 6 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html), [pnpm build-script controls](https://pnpm.io/settings)
- [uv installation](https://docs.astral.sh/uv/getting-started/installation/), [FastAPI releases](https://fastapi.tiangolo.com/release-notes/), [SQLAlchemy](https://docs.sqlalchemy.org/en/20/), [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Go distributions](https://go.dev/dl/), [Paper project setup](https://docs.papermc.io/paper/dev/project-setup/), [Gradle Java compatibility](https://docs.gradle.org/current/userguide/compatibility.html)
- [PostgreSQL support](https://www.postgresql.org/support/versioning/), [PostgreSQL container persistence](https://docs.docker.com/guides/postgresql/immediate-setup-and-data-persistence/)
- [Redis 8.10.1 license source](https://github.com/redis/redis/blob/8.10.1/LICENSE.txt), [Caddy releases](https://github.com/caddyserver/caddy/releases)

Dependency updates must regenerate locks, pass peer checks, conformance/tests/builds and scans, and document any platform/support change. No floating `latest` image tag is used.
