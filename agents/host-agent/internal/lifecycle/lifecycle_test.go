package lifecycle

import (
	"context"
	"io"
	"log/slog"
	"testing"
	"time"
)

func TestCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan struct{})
	go func() { Run(ctx, slog.New(slog.NewJSONHandler(io.Discard, nil))); close(done) }()
	cancel()
	select {
	case <-done:
	case <-time.After(time.Second):
		t.Fatal("shutdown did not finish")
	}
}
