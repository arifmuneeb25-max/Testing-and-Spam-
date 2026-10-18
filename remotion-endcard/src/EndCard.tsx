import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {Grain} from './components/Grain';
import {TypeLayer} from './TypeLayer';
import {COLORS, PLATE} from './theme';

/** The full card: plate, black fade up, type, grain. */
export const EndCard: React.FC = () => {
  const frame = useCurrentFrame();

  // The plate eases to rest around the bare patch, and is dead still from
  // frame 80 on.
  const scale = interpolate(
    frame,
    [0, PLATE.settleEnd],
    [PLATE.settleFrom, PLATE.settleTo],
    {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    },
  );

  const blackout = interpolate(frame, [0, PLATE.fadeOutEnd], [1, 0], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.black}}>
      <AbsoluteFill style={{zIndex: 0}}>
        <Img
          src={staticFile('endcard_plate.png')}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${scale})`,
            transformOrigin: PLATE.origin,
          }}
        />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          zIndex: 1,
          backgroundColor: COLORS.black,
          opacity: blackout,
        }}
      />

      <AbsoluteFill style={{zIndex: 2}}>
        <TypeLayer />
      </AbsoluteFill>

      <AbsoluteFill style={{zIndex: 3}}>
        <Grain />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
