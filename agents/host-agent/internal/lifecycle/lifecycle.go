package lifecycle

import (
	"context"
	"log/slog"
)

// Run waits for local shutdown only. It does not connect to a control plane.
func Run(ctx context.Context, logger *slog.Logger) {
	logger.Info("agent.started", "mode", "foundation")
	<-ctx.Done()
	logger.Info("agent.stopped")
}
