import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('png');
Config.setOverwriteOutput(true);
// EndCardAlpha needs a transparent canvas; the plate composition paints its own
// background, so a transparent default is safe for both.
Config.setChromiumOpenGlRenderer('angle');
