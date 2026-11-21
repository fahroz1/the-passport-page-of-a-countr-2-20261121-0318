// The Passport Page of a Country That Isn't There.
// Entry program: copies the pre-rendered invented passport spread
// (entry.png, committed in this repository) to the output directory
// as /output/entry.png. No network, Node 22 stdlib only.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(scriptDir, "entry.png");
const outputDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const targetPath = join(outputDir, "entry.png");

// The PNG magic bytes: a whole PNG must start with them.
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message: string): never {
  console.error(`entry: ${message}`);
  process.exit(1);
}

if (!existsSync(sourcePath)) {
  fail(`source image not found: ${sourcePath}`);
}

const size = statSync(sourcePath).size;
if (size === 0) {
  fail(`source image is empty: ${sourcePath}`);
}
if (size > 1_048_576) {
  fail(`source image is ${size} bytes, over the 1,048,576 byte cap`);
}

const header = readFileSync(sourcePath).subarray(0, 8);
if (!header.equals(PNG_SIGNATURE)) {
  fail(`source image is not a PNG: ${sourcePath}`);
}

mkdirSync(outputDir, { recursive: true });

try {
  copyFileSync(sourcePath, targetPath);
} catch (error) {
  fail(`could not copy ${sourcePath} to ${targetPath}: ${String(error)}`);
}

const copiedSize = statSync(targetPath).size;
if (copiedSize !== size) {
  fail(`copied size mismatch: ${copiedSize} bytes, expected ${size}`);
}

console.log(`entry: wrote ${targetPath} (${copiedSize} bytes)`);
