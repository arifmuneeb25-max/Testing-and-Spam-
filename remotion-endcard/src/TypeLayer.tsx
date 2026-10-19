import React from 'react';
import {AbsoluteFill} from 'remotion';
import {ACCENT_WEIGHT, ALMARAI, BODY_WEIGHT, INSTRUMENT_SERIF} from './fonts';
import {Ghost} from './components/Ghost';
import {Scrim} from './components/Scrim';
import {Word, wordLayoutStyle} from './components/Word';
import {
  COLORS,
  GHOST_ANCHOR_INDEX,
  GHOSTS,
  LAYOUT,
  LINE_1,
  LINE_2,
  LINE_3,
  SHADOW,
  STOP,
} from './theme';

/**
 * A line of type whose vertical centre sits on y. Every line is laid out at
 * its final resting position, then each word animates in from an offset, so
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
      fontWeight: BODY_WEIGHT,
      fontSize: LAYOUT.bodySize,
      letterSpacing: 0,
    }}
  >
    {children}
  </div>
);

/** An ivory Almarai word on the standard reveal. Lines 1 to 3 are all this. */
const BodyWord: React.FC<{text: string; start: number}> = ({text, start}) => (
  <Word
    start={start}
    fontFamily={ALMARAI}
    fontSize={LAYOUT.bodySize}
    fontWeight={BODY_WEIGHT}
    color={COLORS.ivory}
    textShadow={SHADOW.ivory}
    letterSpacing={LAYOUT.bodyTracking}
  >
    {text}
  </Word>
);

/**
 * A copy of line 1 with every word invisible but still measured, carrying the
 * ghost stack under "lose". Sits below the type and above the scrim.
 */
const GhostLayer: React.FC = () => (
  <Line y={LAYOUT.line1Y} zIndex={1}>
    {LINE_1.map((word, i) => (
      <React.Fragment key={word.text}>
        {i > 0 ? ' ' : null}
        <span
          style={{
            ...wordLayoutStyle(
              ALMARAI,
              LAYOUT.bodySize,
              BODY_WEIGHT,
              LAYOUT.bodyTracking,
            ),
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
                  fontWeight={BODY_WEIGHT}
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

/** Scrim, ghosts and all three lines. No plate, no dim, no fade, no grain. */
export const TypeLayer: React.FC = () => (
  <AbsoluteFill
    style={{
      WebkitFontSmoothing: 'antialiased',
      textRendering: 'optimizeLegibility',
      fontKerning: 'normal',
    }}
  >
    <AbsoluteFill style={{zIndex: 0}}>
      <Scrim />
    </AbsoluteFill>

    <GhostLayer />

    <Line y={LAYOUT.line1Y} zIndex={2}>
      {LINE_1.map((word, i) => (
        <React.Fragment key={word.text}>
          {i > 0 ? ' ' : null}
          <BodyWord text={word.text} start={word.start} />
        </React.Fragment>
      ))}
    </Line>

    <Line y={LAYOUT.line2Y} zIndex={2}>
      {LINE_2.map((word, i) => (
        <React.Fragment key={word.text}>
          {i > 0 ? ' ' : null}
          <BodyWord text={word.text} start={word.start} />
        </React.Fragment>
      ))}
    </Line>

    <Line y={LAYOUT.line3Y} zIndex={2}>
      {LINE_3.map((word) => (
        <React.Fragment key={word.text}>
          <BodyWord text={word.text} start={word.start} />{' '}
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
        fontWeight={ACCENT_WEIGHT}
        color={COLORS.gold}
        textShadow={SHADOW.gold}
        letterSpacing={LAYOUT.accentTracking}
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
