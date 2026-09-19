FROM node:26.8.2-alpine3.24@sha256:ef24c5053d50fdc3e4e56eb4e7ddb7861874ab0fdc797046ba897581deb8e868 AS build
RUN npm install --global pnpm@12.4.2
WORKDIR /app
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json apps/web/package.json
COPY packages/api-client/package.json packages/api-client/package.json
RUN pnpm install --frozen-lockfile
COPY apps/web apps/web
COPY packages/api-client packages/api-client
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm --filter @platform/web build

FROM node:26.8.2-alpine3.24@sha256:ef24c5053d50fdc3e4e56eb4e7ddb7861874ab0fdc797046ba897581deb8e868 AS runtime
# zlib-ng 2.3.3 supplies a separate ABI and has no CVE-2026-85091 match.
# Node retains its required libz ABI through the explicit compatibility link.
RUN apk add --no-cache zlib-ng \
    && apk del zlib apk-tools \
    && ln -s /usr/lib/libz-ng.so.2 /usr/local/lib/libz.so.1 \
    && test ! -e /usr/lib/libz.so.1 \
    && node -e 'const zlib = require("node:zlib"); const data = Buffer.alloc(1024 * 1024, 7); if (!zlib.gunzipSync(zlib.gzipSync(data)).equals(data)) process.exit(1)'
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
WORKDIR /app
COPY --from=build --chown=node:node /app/apps/web/.next/standalone ./
COPY --from=build --chown=node:node /app/apps/web/.next/static ./apps/web/.next/static
RUN rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack
USER node
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
