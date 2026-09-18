# Dependency research and selection

Research date: 2026-09-18. These are **proposed version lines**, not installed dependencies or a tested compatibility matrix. Official pages were consulted during design. Exact package patches, image digests, transitive licenses and build compatibility must be resolved in Phase 1 before implementation uses them. Do not put floating `latest` tags in committed deployment files.

| Component | Proposed baseline / observed evidence | Official reference |
| --- | --- | --- |
| Node.js | 24 LTS; prefer LTS over 26 Current | [Release schedule](https://nodejs.org/en/about/previous-releases) |
| Next.js | Supported stable 16.x, exact security patch to resolve | [Installation requirements](https://nextjs.org/docs/app/getting-started/installation) |
| React | 19.x matching Next peer requirements; version page reports 19.3 | [Versions](https://react.dev/versions) |
| TypeScript | Supported stable compiler compatible with Next/ESLint; 6.0 documentation reviewed, final line unresolved | [Release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html) |
| Tailwind | 4.x; use Next/PostCSS integration in implementation | [Official installation documentation](https://tailwindcss.com/docs/installation/using-vite) |
| Python | 3.14 line; official downloads surfaced 3.14.6, recheck patch on lock | [Downloads](https://www.python.org/getit/) |
| FastAPI | Current stable release compatible with Python/Pydantic; exact version unresolved | [Release notes](https://fastapi.tiangolo.com/release-notes/) |
| Pydantic | 2.x; align with selected FastAPI | [Documentation](https://docs.pydantic.dev/latest/) |
| SQLAlchemy | 2.0 line; official page reports 2.0.54 | [Documentation](https://docs.sqlalchemy.org/en/20/) |
| Alembic | 1.x; official documentation reports 1.20.0 | [Documentation](https://alembic.sqlalchemy.org/en/latest/) |
| PostgreSQL | 18, latest supported minor at lock; versioning page reports 18.6 | [Supported versions](https://www.postgresql.org/support/versioning/) |
| Redis | Supported 8.x OSS line; exact release and license election unresolved | [Official security support](https://github.com/redis/redis/security), [release index](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/) |
| Go | 1.27.1 observed on official downloads; verify supported platforms | [Downloads](https://go.dev/dl/) |
| Paper / Java | Current documented Paper 26.x and Java 25; pin exact published API/build later | [Requirements](https://docs.papermc.io/paper/getting-started/), [plugin setup](https://docs.papermc.io/paper/dev/project-setup/) |
| Gradle | Stable 9.x matching Java 25; Java 25 execution requires at least 9.1 | [Compatibility matrix](https://docs.gradle.org/current/userguide/compatibility.html) |
| Caddy | Stable 2.x; exact version/digest unresolved | [Documentation](https://caddyserver.com/docs/) |
| Docker / Compose | Supported Engine/Desktop and Compose plugin; exact minimum unresolved | [Compose documentation](https://docs.docker.com/compose/) |

The pages above can update independently and search snapshots may lag. Observed patch numbers are research evidence, not a release lock or a guarantee of currentness. Verify registry releases, security advisories, platform support and published image digests when writing manifests. Official Next documentation requires Node >=20.9 and notes that Next 16 builds do not run lint automatically; use an explicit lint CI job. Go downloads list Darwin amd64 and Linux amd64/arm64; confirm the actual Mac's OS meets the selected toolchain requirements.

## Dependency admission and licenses

Record name/version, purpose, source, maintenance evidence, license/SPDX identifier and alternatives for each significant direct dependency when introducing it. Prefer standard libraries for protocol framing, fixed process execution and cryptographic primitives. Use maintained libraries for password hashing, database drivers and framework integration rather than bespoke implementations.

Expected dependencies include a PostgreSQL driver, Redis client, Argon2id library, Go WebSocket client, host-metrics collector and local journal storage. These are proposals, not selected packages. Compare platform support and maintenance before choosing them. Use native testing: pytest, frontend component tests, Playwright, Go tests and JUnit; pin tool versions and browser images. pnpm and uv are proposed lockfile tooling, subject to compatibility verification.

Redis distribution/license selection and Paper API/distribution obligations need explicit recording before shipping. This document does not assert legal suitability of unreviewed dependency versions. Do not introduce experimental dependencies, a full queue framework or an additional UI framework without a concrete need.

## Phase 1 compatibility gate

Resolve and lock all direct/transitive dependencies, build each component, check native wheels for Python 3.14 on Linux and Intel macOS, confirm Next/React/TypeScript peers, run plugin compile/tests with pinned Java/Paper/Gradle, build architecture-specific images and inspect scans. If a stable version fails compatibility, select a supported earlier line and document evidence. These checks are intentionally unrun in this documentation-only phase.
