import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {GHOST, GHOSTS_END} from '../theme';

export type GhostProps = {
  children: string;
  start: number;
  /** Resting distance below the anchor word, in px. */
  offsetY: number;
  peak: number;
  blur: number;
  fontFamily: string;
  fontSize: number;
  color: string;
  letterSpacing: number;
};

/**
 * One failure stacked behind "lose". Same text, font, size, colour and x as the
 * word itself, sitting on a layer below the type so it can never read as
 * foreground.
 */
export const Ghost: React.FC<GhostProps> = ({
  children,
  start,
  offsetY,
  peak,
  blur,
  fontFamily,
  fontSize,
  color,
  letterSpacing,
}) => {
  const frame = useCurrentFrame();

  const riseEnd = start + GHOST.rise;
  const holdEnd = riseEnd + GHOST.hold;

  const opacity = interpolate(
    frame,
    [start, riseEnd, holdEnd, GHOSTS_END],
    [0, peak, peak, 0],
    {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    },
  );

  // Drifts a further 8px down while it fades. Linear, no easing.
  const drift = interpolate(frame, [holdEnd, GHOSTS_END], [0, GHOST.drift], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <span
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        whiteSpace: 'nowrap',
        visibility: 'visible',
        fontFamily,
        fontWeight: 400,
        fontSize,
        color,
        letterSpacing: `${letterSpacing}em`,
        opacity,
        transform: `translateY(${offsetY + drift}px)`,
        filter: `blur(${blur}px)`,
      }}
    >
      {children}
    </span>
  );
};
