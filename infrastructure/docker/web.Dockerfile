FROM node:24.21.0-trixie-slim@sha256:d7b4e5c4ad20b327d7bb16fab6aecd60ac20aa50f8514eb75a2b059e89abe48e AS build
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

FROM node:24.21.0-trixie-slim@sha256:d7b4e5c4ad20b327d7bb16fab6aecd60ac20aa50f8514eb75a2b059e89abe48e AS runtime
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
WORKDIR /app
COPY --from=build --chown=node:node /app/apps/web/.next/standalone ./
COPY --from=build --chown=node:node /app/apps/web/.next/static ./apps/web/.next/static
RUN rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack
USER node
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
