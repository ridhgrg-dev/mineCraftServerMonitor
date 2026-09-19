package version

var Version = "0.1.0"
var Commit = "development"
var BuiltAt = "unknown"

type Info struct {
	Version string `json:"version"`
	Commit  string `json:"commit"`
	BuiltAt string `json:"built_at"`
}

func Current() Info { return Info{Version, Commit, BuiltAt} }
