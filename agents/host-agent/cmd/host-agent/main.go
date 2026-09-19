package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"github.com/ridhgrg-dev/mineCraftServerMonitor/agents/host-agent/internal/config"
	"github.com/ridhgrg-dev/mineCraftServerMonitor/agents/host-agent/internal/lifecycle"
	"github.com/ridhgrg-dev/mineCraftServerMonitor/agents/host-agent/internal/version"
)

func main() {
	showVersion := flag.Bool("version", false, "Print build information as JSON")
	configPath := flag.String("config", "", "Path to local JSON configuration")
	flag.Parse()
	if flag.NArg() != 0 {
		fmt.Fprintln(os.Stderr, "unsupported positional arguments")
		os.Exit(2)
	}
	if *showVersion {
		if err := json.NewEncoder(os.Stdout).Encode(version.Current()); err != nil {
			os.Exit(1)
		}
		return
	}
	cfg, err := config.Load(*configPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Invalid configuration:", err)
		os.Exit(2)
	}
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: cfg.Level()}))
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer cancel()
	lifecycle.Run(ctx, logger)
}
