import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {ALMARAI, INSTRUMENT_SERIF} from './fonts';
import {Ghost} from './components/Ghost';
import {Word, wordLayoutStyle} from './components/Word';
import {
  COLORS,
  EYEBROW,
  GHOST_ANCHOR_INDEX,
  GHOSTS,
  LAYOUT,
  LINE_1,
  LINE_2,
  SHADOW,
  STOP,
} from './theme';

/**
 * A line of type whose vertical centre sits on y. Both lines are laid out at
 * their final resting positions, then each word animates in from an offset, so
 * nothing ever pushes or reflows a neighbour.
 */
const Line: React.FC<{
  y: number;
  zIndex: number;
  children: React.ReactNode;
}> = ({y, zIndex, children}) => (
  <div
    style={{
      position: 'absolute',
      left: 0,
      right: 0,
      top: y,
      transform: 'translateY(-50%)',
      textAlign: 'center',
      whiteSpace: 'nowrap',
      lineHeight: 1.15,
      zIndex,
      // The spaces between the words are text nodes on this element, so it
      // carries the body metrics. Without it they fall back to the root size
      // and the words sit almost on top of each other.
      fontFamily: ALMARAI,
      fontSize: LAYOUT.bodySize,
      letterSpacing: 0,
    }}
  >
    {children}
  </div>
);

const Eyebrow: React.FC = () => {
  const frame = useCurrentFrame();
  const options = {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  } as const;

  const opacity = interpolate(
    frame,
    [EYEBROW.start, EYEBROW.end],
    [0, EYEBROW.opacity],
    options,
  );
  const tracking = interpolate(
    frame,
    [EYEBROW.start, EYEBROW.end],
    [LAYOUT.eyebrowTrackingStart, LAYOUT.eyebrowTracking],
    options,
  );

  // No movement, no blur. Only the opacity and the tracking.
  return (
    <Line y={LAYOUT.eyebrowY} zIndex={3}>
      <span
        style={{
          display: 'inline-block',
          fontFamily: ALMARAI,
          fontWeight: 400,
          fontSize: LAYOUT.eyebrowSize,
          color: COLORS.muted,
          textTransform: 'uppercase',
          letterSpacing: `${tracking}em`,
          marginRight: `${-tracking}em`,
          opacity,
        }}
      >
        {EYEBROW.text}
      </span>
    </Line>
  );
};

/**
 * A copy of line 1 with every word invisible but still measured, carrying the
 * ghost stack under "lose". Lives below the type layer.
 */
const GhostLayer: React.FC = () => (
  <Line y={LAYOUT.line1Y} zIndex={1}>
    {LINE_1.map((word, i) => (
      <React.Fragment key={word.text}>
        {i > 0 ? ' ' : null}
        <span
          style={{
            ...wordLayoutStyle(ALMARAI, LAYOUT.bodySize, LAYOUT.bodyTracking),
            position: i === GHOST_ANCHOR_INDEX ? 'relative' : 'static',
            visibility: 'hidden',
          }}
        >
          {word.text}
          {i === GHOST_ANCHOR_INDEX
            ? GHOSTS.map((ghost) => (
                <Ghost
                  key={ghost.start}
                  start={ghost.start}
                  offsetY={ghost.offsetY}
                  peak={ghost.peak}
                  blur={ghost.blur}
                  fontFamily={ALMARAI}
                  fontSize={LAYOUT.bodySize}
                  color={COLORS.ivory}
                  letterSpacing={LAYOUT.bodyTracking}
                >
                  {word.text}
                </Ghost>
              ))
            : null}
        </span>
      </React.Fragment>
    ))}
  </Line>
);

/** Eyebrow, both headlines and the ghosts. No plate, no fade, no grain. */
export const TypeLayer: React.FC = () => (
  <AbsoluteFill
    style={{
      WebkitFontSmoothing: 'antialiased',
      textRendering: 'optimizeLegibility',
      // Subpixel positioning: lets the words land on fractional pixels instead
      // of snapping, which is what keeps the reveal from stepping.
      fontKerning: 'normal',
    }}
  >
    <Eyebrow />
    <GhostLayer />

    <Line y={LAYOUT.line1Y} zIndex={2}>
      {LINE_1.map((word, i) => (
        <React.Fragment key={word.text}>
          {i > 0 ? ' ' : null}
          <Word
            start={word.start}
            fontFamily={ALMARAI}
            fontSize={LAYOUT.bodySize}
            color={COLORS.ivory}
            textShadow={SHADOW.ivory}
            letterSpacing={LAYOUT.bodyTracking}
          >
            {word.text}
          </Word>
        </React.Fragment>
      ))}
    </Line>

    <Line y={LAYOUT.line2Y} zIndex={2}>
      {LINE_2.map((word) => (
        <React.Fragment key={word.text}>
          <Word
            start={word.start}
            fontFamily={ALMARAI}
            fontSize={LAYOUT.bodySize}
            color={COLORS.ivory}
            textShadow={SHADOW.ivory}
            letterSpacing={LAYOUT.bodyTracking}
          >
            {word.text}
          </Word>{' '}
        </React.Fragment>
      ))}
      <Word
        start={STOP.start}
        durationInFrames={STOP.revealDuration}
        blur={STOP.blur}
        translateY={STOP.translateY}
        fontFamily={INSTRUMENT_SERIF}
        fontStyle="italic"
        fontSize={LAYOUT.accentSize}
        color={COLORS.gold}
        textShadow={SHADOW.gold}
        letterSpacing={0}
        drift={{
          from: STOP.driftFrom,
          to: STOP.driftTo,
          scaleTo: STOP.scaleTo,
          translateXTo: STOP.translateXTo,
        }}
      >
        {STOP.text}
      </Word>
    </Line>
  </AbsoluteFill>
);
