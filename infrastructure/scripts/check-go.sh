#!/bin/sh
set -eu
cd agents/host-agent
[ -z "$(gofmt -l .)" ]
go vet ./...
go test ./...
go test -race ./...
mkdir -p build
for target in linux/amd64 linux/arm64 darwin/amd64; do
  target_os=${target%/*}
  target_arch=${target#*/}
  GOOS="$target_os" GOARCH="$target_arch" CGO_ENABLED=0 go build -trimpath -o "build/host-agent-$target_os-$target_arch" ./cmd/host-agent
done
