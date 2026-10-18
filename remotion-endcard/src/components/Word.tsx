import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {REVEAL} from '../theme';

/** Shared easing. No spring, no overshoot, clamped at both ends. */
export const EASE = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * The box model a word occupies at rest. The ghost layer reuses it so its
 * mirror of line 1 lays out to the pixel, which is how the ghosts inherit the
 * exact x of "lose" without a magic number.
 *
 * letterSpacing leaves a trailing space after the last glyph, which would push
 * a centred line off centre by half of it. The negative margin takes it back.
 */
export const wordLayoutStyle = (
  fontFamily: string,
  fontSize: number,
  letterSpacing: number,
  fontStyle: 'normal' | 'italic' = 'normal',
): React.CSSProperties => ({
  display: 'inline-block',
  fontFamily,
  fontStyle,
  fontWeight: 400,
  fontSize,
  letterSpacing: `${letterSpacing}em`,
  marginRight: `${-letterSpacing}em`,
});

export type Drift = {
  from: number;
  to: number;
  scaleTo: number;
  translateXTo: number;
};

export type WordProps = {
  children: string;
  /** Frame the reveal begins on. */
  start: number;
  fontFamily: string;
  fontSize: number;
  color: string;
  textShadow: string;
  /** In em. The trailing space it adds is compensated so lines centre true. */
  letterSpacing: number;
  fontStyle?: 'normal' | 'italic';
  durationInFrames?: number;
  blur?: number;
  translateY?: number;
  /** Only "stop." uses this: a linear move that is still running on frame 119. */
  drift?: Drift;
};

export const Word: React.FC<WordProps> = ({
  children,
  start,
  fontFamily,
  fontSize,
  color,
  textShadow,
  letterSpacing,
  fontStyle = 'normal',
  durationInFrames = REVEAL.durationInFrames,
  blur = REVEAL.blur,
  translateY = REVEAL.translateY,
  drift,
}) => {
  const frame = useCurrentFrame();
  const range: [number, number] = [start, start + durationInFrames];
  const options = {
    easing: EASE,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  } as const;

  const opacity = interpolate(frame, range, [0, 1], options);
  const y = interpolate(frame, range, [translateY, 0], options);
  const blurPx = interpolate(frame, range, [blur, 0], options);

  // Linear, extrapolated right, so the velocity on the last frame is the same
  // as the velocity on the first. The word never settles.
  const driftRange: [number, number] = drift
    ? [drift.from, drift.to]
    : [0, 1];
  const driftOptions = {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'extend',
  } as const;
  const x = drift
    ? interpolate(frame, driftRange, [0, drift.translateXTo], driftOptions)
    : 0;
  const scale = drift
    ? interpolate(frame, driftRange, [1, drift.scaleTo], driftOptions)
    : 1;

  return (
    <span
      style={{
        ...wordLayoutStyle(fontFamily, fontSize, letterSpacing, fontStyle),
        color,
        textShadow,
        opacity,
        transform: `translateX(${x}px) translateY(${y}px) scale(${scale})`,
        transformOrigin: 'left center',
        filter: `blur(${blurPx}px)`,
        willChange: 'transform, opacity, filter',
      }}
    >
      {children}
    </span>
  );
};
