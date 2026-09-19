# Host agent foundation

`go run ./cmd/host-agent --version` prints build metadata. `go run ./cmd/host-agent --config config.json` accepts only local `log_level` configuration and waits for SIGINT/SIGTERM. No network connection, enrollment, telemetry or runtime control exists yet. Docker/systemd are the approved future adapter targets; manual process lifecycle control requires separate review. Standard-library-only module; no go.sum is needed until dependencies exist.
