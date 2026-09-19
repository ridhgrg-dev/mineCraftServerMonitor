package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoad(t *testing.T) {
	for _, tc := range []struct {
		name, body string
		valid      bool
	}{
		{"valid", `{"log_level":"warn"}`, true},
		{"unknown", `{"execute_shell":"anything"}`, false},
		{"level", `{"log_level":"secret"}`, false},
		{"trailing", `{} {}`, false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			p := filepath.Join(t.TempDir(), "config.json")
			if err := os.WriteFile(p, []byte(tc.body), 0600); err != nil {
				t.Fatal(err)
			}
			_, err := Load(p)
			if (err == nil) != tc.valid {
				t.Fatalf("unexpected result: %v", err)
			}
		})
	}
}
func TestDefaults(t *testing.T) {
	c, err := Load("")
	if err != nil || c.LogLevel != "info" {
		t.Fatal(c, err)
	}
}
