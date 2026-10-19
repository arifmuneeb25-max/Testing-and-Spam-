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

/** The full card: plate, dim, scrim, type, black fade up, grain. */
export const EndCard: React.FC = () => {
  const frame = useCurrentFrame();

  const ease = {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  } as const;

  // The plate eases to rest around the bare patch, and is dead still from
  // frame 80 on.
  const scale = interpolate(
    frame,
    [0, PLATE.settleEnd],
    [PLATE.settleFrom, PLATE.settleTo],
    ease,
  );

  // Knocked back so the words have somewhere to sit, then held there.
  const brightness = interpolate(
    frame,
    [PLATE.dimStart, PLATE.dimEnd],
    [PLATE.dimFrom, PLATE.dimTo],
    ease,
  );

  const blackout = interpolate(frame, [0, PLATE.fadeOutEnd], [1, 0], ease);

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
            filter: `brightness(${brightness})`,
          }}
        />
      </AbsoluteFill>

      <AbsoluteFill style={{zIndex: 1}}>
        <TypeLayer />
      </AbsoluteFill>

      {/* Over everything, including the type. */}
      <AbsoluteFill
        style={{
          zIndex: 2,
          backgroundColor: COLORS.black,
          opacity: blackout,
        }}
      />

      <AbsoluteFill style={{zIndex: 3}}>
        <Grain />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
