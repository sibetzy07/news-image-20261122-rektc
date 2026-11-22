import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Entry for news-image-20261122: render the day's news image with draw.py
// (pure Python standard library, no network) and write it to the output dir.
const root = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
mkdirSync(outDir, { recursive: true });
const outPath = join(outDir, "entry.png");

const draw = join(root, "draw.py");
let lastError: unknown = null;
for (const python of ["python3", "python"]) {
  try {
    execFileSync(python, [draw, outPath], { stdio: "inherit" });
    lastError = null;
    break;
  } catch (err) {
    lastError = err;
  }
}
if (lastError) {
  throw lastError;
}
