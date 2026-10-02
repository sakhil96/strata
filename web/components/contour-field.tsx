"use client";

import { useEffect, useRef } from "react";

// Contour lines from a seeded value-noise field, traced with marching squares.
// The seed is fixed so the bedrock looks the same on every visit.
function noiseField(seed: number) {
  const perm = new Uint8Array(512);
  let s = seed >>> 0;
  for (let i = 0; i < 256; i++) perm[i] = i;
  for (let i = 255; i > 0; i--) {
    s = (s * 1664525 + 1013904223) >>> 0;
    const j = s % (i + 1);
    [perm[i], perm[j]] = [perm[j], perm[i]];
  }
  for (let i = 0; i < 256; i++) perm[i + 256] = perm[i];
  const lattice = (x: number, y: number) => perm[(perm[x & 255] + y) & 255] / 255;
  const smooth = (t: number) => t * t * (3 - 2 * t);
  const value = (x: number, y: number) => {
    const xi = Math.floor(x);
    const yi = Math.floor(y);
    const u = smooth(x - xi);
    const v = smooth(y - yi);
    const a = lattice(xi, yi);
    const b = lattice(xi + 1, yi);
    const c = lattice(xi, yi + 1);
    const d = lattice(xi + 1, yi + 1);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  };
  return (x: number, y: number) => value(x, y) * 0.6 + value(x * 2.1, y * 2.1) * 0.3 + value(x * 4.3, y * 4.3) * 0.1;
}

export function ContourField({ seed = 20261002 }: { seed?: number }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const field = noiseField(seed);
    const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const levels = 14;
    const cell = 12;
    let frame = 0;
    let raf = 0;

    const draw = (drift: number) => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      if (canvas.width !== w * dpr) {
        canvas.width = w * dpr;
        canvas.height = h * dpr;
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ctx.strokeStyle = "rgba(154, 160, 166, 0.035)";
      ctx.lineWidth = 1;
      const cols = Math.ceil(w / cell) + 1;
      const rows = Math.ceil(h / cell) + 1;
      const grid = new Float32Array(cols * rows);
      for (let j = 0; j < rows; j++)
        for (let i = 0; i < cols; i++) grid[j * cols + i] = field(i * 0.035 + drift, j * 0.035 + drift * 0.4);
      ctx.beginPath();
      for (let l = 1; l < levels; l++) {
        const t = l / levels;
        for (let j = 0; j < rows - 1; j++)
          for (let i = 0; i < cols - 1; i++) {
            const a = grid[j * cols + i];
            const b = grid[j * cols + i + 1];
            const c = grid[(j + 1) * cols + i + 1];
            const d = grid[(j + 1) * cols + i];
            const code = (a > t ? 8 : 0) | (b > t ? 4 : 0) | (c > t ? 2 : 0) | (d > t ? 1 : 0);
            if (code === 0 || code === 15) continue;
            const x = i * cell;
            const y = j * cell;
            const lerp = (p: number, q: number) => (t - p) / (q - p || 1e-6);
            const top: [number, number] = [x + lerp(a, b) * cell, y];
            const right: [number, number] = [x + cell, y + lerp(b, c) * cell];
            const bottom: [number, number] = [x + lerp(d, c) * cell, y + cell];
            const left: [number, number] = [x, y + lerp(a, d) * cell];
            const segs: [number, number][][] = {
              1: [[left, bottom]],
              2: [[bottom, right]],
              3: [[left, right]],
              4: [[top, right]],
              5: [
                [left, top],
                [bottom, right],
              ],
              6: [[top, bottom]],
              7: [[left, top]],
              8: [[left, top]],
              9: [[top, bottom]],
              10: [
                [left, bottom],
                [top, right],
              ],
              11: [[top, right]],
              12: [[left, right]],
              13: [[bottom, right]],
              14: [[left, bottom]],
            }[code] as [number, number][][];
            for (const [p, q] of segs) {
              ctx.moveTo(p[0], p[1]);
              ctx.lineTo(q[0], q[1]);
            }
          }
      }
      ctx.stroke();
    };

    const tick = () => {
      frame += 1;
      if (frame % 3 === 0) draw(frame * 0.0004);
      raf = requestAnimationFrame(tick);
    };
    draw(0);
    if (!still) raf = requestAnimationFrame(tick);
    const onResize = () => draw(frame * 0.0004);
    window.addEventListener("resize", onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
    };
  }, [seed]);

  return <canvas ref={ref} aria-hidden className="pointer-events-none fixed inset-0 -z-10 h-full w-full" />;
}
