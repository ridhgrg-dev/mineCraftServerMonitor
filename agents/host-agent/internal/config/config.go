package config

import (
	"encoding/json"
	"errors"
	"io"
	"log/slog"
	"os"
)

type Config struct {
	LogLevel string `json:"log_level"`
}

func Load(path string) (Config, error) {
	cfg := Config{LogLevel: "info"}
	if path == "" {
		return cfg, nil
	}
	file, err := os.Open(path)
	if err != nil {
		return cfg, errors.New("cannot open configuration file")
	}
	defer file.Close()
	decoder := json.NewDecoder(io.LimitReader(file, 65537))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&cfg); err != nil {
		return cfg, errors.New("expected a JSON object with supported settings")
	}
	var extra any
	if err := decoder.Decode(&extra); err != io.EOF {
		return cfg, errors.New("unexpected trailing configuration")
	}
	switch cfg.LogLevel {
	case "debug", "info", "warn", "error":
	default:
		return cfg, errors.New("unsupported log_level")
	}
	return cfg, nil
}

func (c Config) Level() slog.Level {
	switch c.LogLevel {
	case "debug":
		return slog.LevelDebug
	case "warn":
		return slog.LevelWarn
	case "error":
		return slog.LevelError
	default:
		return slog.LevelInfo
	}
}
