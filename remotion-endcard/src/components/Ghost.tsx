import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {GHOST} from '../theme';

export type GhostProps = {
  children: string;
  start: number;
  /** Resting distance below the anchor word, in px. */
  offsetY: number;
  peak: number;
  blur: number;
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  color: string;
  letterSpacing: number;
};

/**
 * One failure stacked behind "lose". Same text, font, weight, size, colour and
 * x as the word itself, and no shadow, so it reads as an after image of the
 * word rather than another word.
 */
export const Ghost: React.FC<GhostProps> = ({
  children,
  start,
  offsetY,
  peak,
  blur,
  fontFamily,
  fontSize,
  fontWeight,
  color,
  letterSpacing,
}) => {
  const frame = useCurrentFrame();

  const riseEnd = start + GHOST.rise;
  const holdEnd = riseEnd + GHOST.hold;
  const end = holdEnd + GHOST.fall;

  const opacity = interpolate(
    frame,
    [start, riseEnd, holdEnd, end],
    [0, peak, peak, 0],
    {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    },
  );

  // Drifts a further 8px down while it fades. Linear, no easing.
  const drift = interpolate(frame, [holdEnd, end], [0, GHOST.drift], {
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
        fontWeight,
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
