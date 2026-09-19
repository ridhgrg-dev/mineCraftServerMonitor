FROM ghcr.io/astral-sh/uv:0.12.17 AS uv
FROM python:3.14.7-alpine3.24@sha256:016508ba505da24f7139765bc4bb669df4e88eb2f12eeadd571bf2f88d7533df AS compression
RUN apk add --no-cache build-base cmake curl
# zlib-ng's compatibility ABI preserves Python compression without the zlib
# gz_vacate implementation affected by CVE-2026-85091.
RUN curl -fsSL https://github.com/zlib-ng/zlib-ng/archive/refs/tags/2.3.3.tar.gz -o /tmp/zlib-ng.tar.gz \
    && echo 'f9c65aa9c852eb8255b636fd9f07ce1c406f061ec19a2e7d508b318ca0c907d1  /tmp/zlib-ng.tar.gz' | sha256sum -c - \
    && tar -xzf /tmp/zlib-ng.tar.gz -C /tmp \
    && cmake -S /tmp/zlib-ng-2.3.3 -B /tmp/build -DZLIB_COMPAT=ON -DZLIB_ENABLE_TESTS=ON -DWITH_GTEST=OFF -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/zlib-ng \
    && cmake --build /tmp/build --parallel 2 \
    && ctest --test-dir /tmp/build --output-on-failure \
    && cmake --install /tmp/build
FROM python:3.14.7-alpine3.24@sha256:016508ba505da24f7139765bc4bb669df4e88eb2f12eeadd571bf2f88d7533df AS base
COPY --from=compression /opt/zlib-ng/lib/libz.so* /usr/local/lib/
COPY --from=compression /tmp/zlib-ng-2.3.3/LICENSE.md /usr/local/share/licenses/zlib-ng-2.3.3/LICENSE.md
# Retain every Python runtime dependency except the replaced library. Remove
# apk as well, since its dependency would otherwise retain vulnerable zlib.
RUN apk add --no-cache --virtual .runtime-libs $(apk info -R .python-rundeps | sed -n '/^so:/p' | grep -v '^so:libz.so.1$') \
    && apk del .python-rundeps apk-tools zlib \
    && test ! -e /usr/lib/libz.so.1 \
    && python -c 'import gzip, zlib; data = bytes(range(256)) * 4096; assert zlib.decompress(zlib.compress(data)) == data; assert gzip.decompress(gzip.compress(data)) == data'
COPY --from=uv /uv /usr/local/bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy
WORKDIR /app
COPY apps/api/pyproject.toml apps/api/uv.lock ./
COPY apps/api/src ./src
COPY apps/api/alembic.ini ./
COPY apps/api/migrations ./migrations
RUN uv sync --frozen --no-dev && adduser -D -u 10001 platform
ENV PATH="/app/.venv/bin:$PATH"
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "control_plane.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
