// news-image-20261122: copy the pre-rendered entry.png to the output dir.
//
// Pure Node.js: no network, no subprocess, no Python. The image is rendered
// offline by draw.py (deterministic, stdlib-only) and committed as entry.png
// next to this file; this program only copies those exact bytes, so the
// output is byte-identical on every run.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR || "out");
if (!existsSync(outDir)) {
  mkdirSync(outDir, { recursive: true });
}
copyFileSync(source, join(outDir, "entry.png"));
