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
  /**
   * The eyebrow sits on the lit pool in the centre of the plate. The original
   * #8A94A8 measured 1.15:1 against the bright part of that pool, a near exact
   * value match, which is why it disappeared. Same blue grey, much higher
   * value.
   */
  muted: '#DCE2EB',
  black: '#000000',
} as const;

export const SHADOW = {
  ivory: '0 0 1px rgba(242,237,228,0.35), 0 0 12px rgba(242,237,228,0.10)',
  gold: '0 0 1px rgba(217,164,65,0.4), 0 0 18px rgba(217,164,65,0.22)',
  /**
   * The eyebrow is 24px and widely tracked, so it has little ink to hold the
   * eye against the confetti. A dark halo gives every stroke its own edge, so
   * the line reads against the lit floor instead of competing with it.
   */
  muted: '0 1px 2px rgba(0,0,0,0.60), 0 0 16px rgba(0,0,0,0.70), 0 0 1px rgba(220,226,235,0.30)',
} as const;

/**
 * The three lines keep a fixed rhythm and move as one block. RHYTHM is each
 * line's centre measured down from the eyebrow's centre.
 */
const RHYTHM = {eyebrow: 0, line1: 74, line2: 150} as const;

/**
 * Distance from the eyebrow's centre line down to the optical centre of the
 * whole block, measured off a render rather than guessed: the block's ink runs
 * from the eyebrow cap height to the descender of "stop.".
 */
const BLOCK_INK_CENTRE = 101;

/** The block is centred on the frame. Move this one number to reposition it. */
const BLOCK_CENTRE_Y = HEIGHT / 2;

const BLOCK_TOP = BLOCK_CENTRE_Y - BLOCK_INK_CENTRE;

/** Vertical centre of each line, in pixels from the top of the frame. */
export const LAYOUT = {
  eyebrowY: BLOCK_TOP + RHYTHM.eyebrow,
  line1Y: BLOCK_TOP + RHYTHM.line1,
  line2Y: BLOCK_TOP + RHYTHM.line2,
  eyebrowSize: 24,
  bodySize: 62,
  accentSize: 65,
  eyebrowTracking: 0.28, // em, resting
  eyebrowTrackingStart: 0.4, // em, at frame 8
  bodyTracking: -0.01, // em
} as const;

/** The standard reveal, shared by every headline word unless stated otherwise. */
export const REVEAL = {
  durationInFrames: 10,
  translateY: 12,
  blur: 10,
} as const;

export const PLATE = {
  fadeOutEnd: 12, // black layer 1 -> 0
  settleEnd: 80, // scale 1.040 -> 1.000
  settleFrom: 1.04,
  settleTo: 1.0,
  origin: '50% 62%', // the bare patch in the lower centre
} as const;

export const EYEBROW = {
  start: 8,
  end: 32,
  opacity: 0.85,
  text: 'A CONCEPT BY MUNEEB ARIF',
} as const;

/** Line 1, with the start frame of each word's reveal. */
export const LINE_1: {text: string; start: number}[] = [
  {text: 'Winners', start: 14},
  {text: 'lose', start: 19},
  {text: 'more', start: 24},
  {text: 'than', start: 31},
  {text: 'losers', start: 35},
  {text: 'ever', start: 39},
  {text: 'will.', start: 43},
];

/** Index of the word the ghosts stack under. */
export const GHOST_ANCHOR_INDEX = 1; // "lose"

/**
 * The failures stacking up behind "lose".
 *
 * The brief asks for a 14 frame fade on each ghost, which would leave ghost 3
 * alive until frame 53 and bleed into the held beat. The hard constraint is
 * that the stack is gone by GHOSTS_END, so the fade length is derived from it
 * and the 4 frame rise and 4 frame hold are kept exactly.
 */
export const GHOSTS_END = 50;

export const GHOSTS: {
  start: number;
  offsetY: number;
  peak: number;
  blur: number;
}[] = [
  {start: 27, offsetY: 30, peak: 0.25, blur: 1},
  {start: 29, offsetY: 58, peak: 0.15, blur: 2},
  {start: 31, offsetY: 84, peak: 0.08, blur: 3},
];

export const GHOST = {
  rise: 4,
  hold: 4,
  drift: 8, // extra px travelled while fading out
} as const;

/** Line 2. "stop." is handled separately, it does not take the standard reveal. */
export const LINE_2: {text: string; start: number}[] = [
  {text: 'They', start: 64},
  {text: 'just', start: 68},
  {text: "don't", start: 72},
];

export const STOP = {
  text: 'stop.',
  start: 80,
  revealDuration: 14,
  blur: 14,
  translateY: 12,
  /** The drift that never resolves. Linear, still moving on the last frame. */
  driftFrom: 80,
  driftTo: 119,
  scaleTo: 1.03,
  translateXTo: 10,
} as const;

export const GRAIN = {
  opacity: 0.06,
  /** 1 means one noise sample per output pixel. */
  pixelSize: 1,
} as const;
