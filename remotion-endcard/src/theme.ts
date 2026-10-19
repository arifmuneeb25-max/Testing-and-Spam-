/**
 * Every number the end card uses. Nothing in the animation is hard coded
 * anywhere else, so the whole piece can be retimed from this one file.
 */

export const FPS = 24;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const DURATION_IN_FRAMES = 120; // frames 0 to 119

export const COLORS = {
  ivory: '#F2EDE4',
  gold: '#D9A441',
  inkNavy: '#0B1120',
  black: '#000000',
} as const;

/**
 * A dark halo under every word. The plate has a pool of light in the middle of
 * it, so a light glow would do nothing. The type is lit from the front and the
 * background falls away behind it.
 */
export const SHADOW = {
  ivory: '0 2px 3px rgba(11,17,32,0.55), 0 4px 28px rgba(11,17,32,0.85)',
  gold:
    '0 2px 3px rgba(11,17,32,0.55), 0 4px 28px rgba(11,17,32,0.85), 0 0 22px rgba(217,164,65,0.28)',
  none: 'none',
} as const;

/**
 * Vertical centre of each line, in pixels from the top of the frame.
 *
 * The gap from line 2 to line 3 is 144px against 106px between lines 1 and 2.
 * Lines 1 and 2 are one thought, line 3 is the answer, and the space says so.
 */
export const LAYOUT = {
  line1Y: 420,
  line2Y: 526,
  line3Y: 670,
  bodySize: 96,
  accentSize: 116,
  bodyTracking: -0.015, // em
  accentTracking: 0, // em
} as const;

/** The standard reveal, shared by every word unless stated otherwise. */
export const REVEAL = {
  durationInFrames: 10,
  translateY: 16,
  blur: 12,
} as const;

export const PLATE = {
  fadeOutEnd: 12, // the black layer over everything, 1 -> 0
  settleEnd: 80, // scale 1.040 -> 1.000
  settleFrom: 1.04,
  settleTo: 1.0,
  origin: '50% 62%', // the bare patch in the lower centre
  /** Brightness knocked back so the type has somewhere to sit. */
  dimStart: 8,
  dimEnd: 24,
  dimFrom: 1.0,
  dimTo: 0.62,
} as const;

export const SCRIM = {
  start: 8,
  end: 24,
  width: 1500,
  height: 620,
  centre: 'rgba(11,17,32,0.78)',
  edge: 'rgba(11,17,32,0)',
} as const;

export const LINE_1: {text: string; start: number}[] = [
  {text: 'Winners', start: 14},
  {text: 'lose', start: 19},
  {text: 'more', start: 24},
];

export const LINE_2: {text: string; start: number}[] = [
  {text: 'than', start: 44},
  {text: 'losers', start: 48},
  {text: 'ever', start: 52},
  {text: 'will.', start: 56},
];

/** Line 3 up to but not including "stop.", which has its own reveal. */
export const LINE_3: {text: string; start: number}[] = [
  {text: 'They', start: 74},
  {text: 'just', start: 78},
  {text: "don't", start: 82},
];

/** Index of the word in line 1 the ghosts stack under. */
export const GHOST_ANCHOR_INDEX = 1; // "lose"

/**
 * The failures stacking up behind "lose". They fill the hole where line 2 will
 * land and clear out before it arrives.
 */
export const GHOSTS: {
  start: number;
  offsetY: number;
  peak: number;
  blur: number;
}[] = [
  {start: 26, offsetY: 28, peak: 0.3, blur: 1},
  {start: 28, offsetY: 54, peak: 0.18, blur: 2},
  {start: 30, offsetY: 78, peak: 0.09, blur: 3},
];

export const GHOST = {
  rise: 4,
  hold: 3,
  fall: 10,
  drift: 8, // extra px travelled while fading out
} as const;

export const STOP = {
  text: 'stop.',
  start: 88,
  revealDuration: 14,
  blur: 16,
  translateY: 16,
  /** The drift that never resolves. Linear, still moving on the last frame. */
  driftFrom: 88,
  driftTo: 119,
  scaleTo: 1.035,
  translateXTo: 12,
} as const;

export const GRAIN = {
  opacity: 0.06,
  /** 1 means one noise sample per output pixel. */
  pixelSize: 1,
} as const;
