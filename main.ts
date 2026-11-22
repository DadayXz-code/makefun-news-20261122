// THE WORLD TODAY — news-image-20261122 entry (Node 22, standard library only).
// The front page is drawn by draw.py (Pillow) and committed as entry.png;
// this program copies it to /output/entry.png, mode 0644, and nothing else.
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { chmodSync, copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const out = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(out, { recursive: true });
const dest = join(out, 'entry.png');
copyFileSync(new URL('./entry.png', import.meta.url), dest);
chmodSync(dest, 0o644);
