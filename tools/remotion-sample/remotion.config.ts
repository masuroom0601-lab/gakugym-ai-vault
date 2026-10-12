// See all configuration options: https://remotion.dev/docs/config
// Each option also is available as a CLI flag: https://remotion.dev/docs/cli

// Note: When using the Node.JS APIs, the config file doesn't apply. Instead, pass options directly to the APIs

import { Config } from "@remotion/cli/config";
import { enableTailwind } from '@remotion/tailwind-v4';

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.overrideBundlerConfig(enableTailwind);

// Reuse the Chromium already installed for Playwright in this environment
// instead of letting Remotion try to download its own headless shell.
if (process.env.PLAYWRIGHT_BROWSERS_PATH) {
  Config.setBrowserExecutable(
    `${process.env.PLAYWRIGHT_BROWSERS_PATH}/chromium_headless_shell-1194/chrome-linux/headless_shell`,
  );
}
