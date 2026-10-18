import React, {useLayoutEffect, useRef} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {GRAIN} from '../theme';

/** Small, fast, fully deterministic PRNG. Same seed, same noise, every render. */
const mulberry32 = (seed: number) => {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

/**
 * Monochrome noise regenerated every frame from a seed equal to the frame
 * number, so the grain moves but any given frame is reproducible. Sits above
 * the type, which is what stops the words reading as a layer pasted on top.
 */
export const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const ref = useRef<HTMLCanvasElement>(null);

  const w = Math.ceil(width / GRAIN.pixelSize);
  const h = Math.ceil(height / GRAIN.pixelSize);

  // Layout effect, not effect: the pixels are written before the browser
  // paints, so the frame is never captured with an empty canvas.
  useLayoutEffect(() => {
    const canvas = ref.current;
    if (!canvas) {
      return;
    }
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return;
    }
    const image = ctx.createImageData(w, h);
    // One 32 bit write per pixel instead of four 8 bit ones. Little endian, so
    // the bytes land as ABGR.
    const pixels = new Uint32Array(image.data.buffer);
    const random = mulberry32(frame);
    for (let i = 0; i < pixels.length; i++) {
      const v = (random() * 256) | 0;
      pixels[i] = (255 << 24) | (v << 16) | (v << 8) | v;
    }
    ctx.putImageData(image, 0, 0);
  }, [frame, w, h]);

  return (
    <canvas
      ref={ref}
      width={w}
      height={h}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        opacity: GRAIN.opacity,
        mixBlendMode: 'overlay',
        imageRendering: 'pixelated',
        pointerEvents: 'none',
      }}
    />
  );
};
