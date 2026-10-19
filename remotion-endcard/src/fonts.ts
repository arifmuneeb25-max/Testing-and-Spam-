import {cancelRender, continueRender, delayRender} from 'remotion';
import {loadFont as loadAlmarai} from '@remotion/google-fonts/Almarai';
import {loadFont as loadInstrumentSerif} from '@remotion/google-fonts/InstrumentSerif';

const almarai = loadAlmarai('normal', {weights: ['700'], subsets: ['latin']});
const instrumentSerif = loadInstrumentSerif('italic', {
  weights: ['400'],
  subsets: ['latin'],
});

export const ALMARAI = almarai.fontFamily;
export const INSTRUMENT_SERIF = instrumentSerif.fontFamily;

/** Almarai carries the weight. Instrument Serif has no bold, so "stop." takes
 * its emphasis from size and colour instead. */
export const BODY_WEIGHT = 700;
export const ACCENT_WEIGHT = 400;

/**
 * Held at module scope so the handle exists before the first frame is painted.
 * Nothing renders until both faces are ready, otherwise frame 0 would measure
 * fallback metrics and every line would reflow.
 */
const handle = delayRender('Loading Almarai and Instrument Serif');

Promise.all([almarai.waitUntilDone(), instrumentSerif.waitUntilDone()])
  .then(() => continueRender(handle))
  .catch((err) => cancelRender(err));
