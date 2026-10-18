import {cancelRender, continueRender, delayRender} from 'remotion';
import {loadFont as loadAlmarai} from '@remotion/google-fonts/Almarai';
import {loadFont as loadInstrumentSerif} from '@remotion/google-fonts/InstrumentSerif';

const almarai = loadAlmarai('normal', {weights: ['400'], subsets: ['latin']});
const instrumentSerif = loadInstrumentSerif('italic', {
  weights: ['400'],
  subsets: ['latin'],
});

export const ALMARAI = almarai.fontFamily;
export const INSTRUMENT_SERIF = instrumentSerif.fontFamily;

/**
 * Held at module scope so the handle exists before the first frame is painted.
 * Nothing renders until both faces are ready, otherwise frame 0 would measure
 * fallback metrics and the whole line would reflow.
 */
const handle = delayRender('Loading Almarai and Instrument Serif');

Promise.all([almarai.waitUntilDone(), instrumentSerif.waitUntilDone()])
  .then(() => continueRender(handle))
  .catch((err) => cancelRender(err));
