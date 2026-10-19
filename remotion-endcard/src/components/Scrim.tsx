import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {SCRIM} from '../theme';

/**
 * A soft navy pool behind the type. No edge, no box, no band: a radial
 * gradient that reaches zero alpha well inside the frame, so the stage stays
 * visible around it and the only thing you notice is that the words read.
 */
export const Scrim: React.FC = () => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [SCRIM.start, SCRIM.end], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        opacity,
        background: `radial-gradient(ellipse ${SCRIM.width}px ${SCRIM.height}px at 50% 50%, ${SCRIM.centre} 0%, ${SCRIM.edge} 100%)`,
      }}
    />
  );
};
