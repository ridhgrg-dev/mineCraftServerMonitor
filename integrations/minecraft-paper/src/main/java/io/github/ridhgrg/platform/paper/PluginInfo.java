package io.github.ridhgrg.platform.paper;

/** Pure metadata boundary, independent of a running Paper server. */
public record PluginInfo(String version) {
  public PluginInfo {
    if (version == null || version.isBlank()) {
      throw new IllegalArgumentException("Plugin version is required");
    }
  }
}
