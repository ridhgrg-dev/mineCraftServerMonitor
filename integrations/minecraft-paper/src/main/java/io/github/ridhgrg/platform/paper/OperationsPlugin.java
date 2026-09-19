package io.github.ridhgrg.platform.paper;

import org.bukkit.plugin.java.JavaPlugin;

/** Phase 1 lifecycle only; no telemetry or network transmission. */
public final class OperationsPlugin extends JavaPlugin {
  @Override
  public void onEnable() {
    var info = new PluginInfo(getPluginMeta().getVersion());
    getLogger().info("Server operations integration " + info.version() + " loaded");
  }

  @Override
  public void onDisable() {
    getLogger().info("Server operations integration stopped");
  }
}
