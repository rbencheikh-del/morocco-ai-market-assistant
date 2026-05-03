import { spawnSync } from "node:child_process";

const [workspace, command] = process.argv.slice(2);

if (!workspace || !command) {
  console.error("Usage: node scripts/workspace-run.mjs <workspace> <script>");
  process.exit(1);
}

const npmExecPath = process.env.npm_execpath;

if (!npmExecPath) {
  console.error("Unable to locate npm from npm_execpath.");
  process.exit(1);
}

const result = spawnSync(
  process.execPath,
  [npmExecPath, "--workspace", workspace, "run", command],
  { stdio: "inherit" },
);

process.exit(result.status ?? 1);
