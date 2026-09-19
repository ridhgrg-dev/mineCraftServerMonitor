package io.github.ridhgrg.platform.paper;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;

class PluginInfoTest {
  @Test
  void validatesVersion() {
    assertEquals("0.1.0", new PluginInfo("0.1.0").version());
    assertThrows(IllegalArgumentException.class, () -> new PluginInfo(" "));
    assertThrows(IllegalArgumentException.class, () -> new PluginInfo(null));
  }

  @Test
  void descriptorHasResolvedVersionAndEntrypoint() throws IOException {
    try (var stream = getClass().getResourceAsStream("/plugin.yml")) {
      assertNotNull(stream);
      var descriptor = new String(stream.readAllBytes(), StandardCharsets.UTF_8);
      assertTrue(descriptor.contains("version: '0.1.0'"));
      assertTrue(descriptor.contains("main: io.github.ridhgrg.platform.paper.OperationsPlugin"));
      assertFalse(descriptor.contains("${version}"));
    }
  }
}
