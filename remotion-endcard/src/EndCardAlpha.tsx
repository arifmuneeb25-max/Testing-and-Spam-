import React from 'react';
import {AbsoluteFill} from 'remotion';
import {TypeLayer} from './TypeLayer';

/**
 * Text, ghosts and scrim on the same timeline, with nothing else: no plate, no
 * plate dim, no black fade and no grain, on a transparent background, so the
 * card can be built over the plate in an edit instead.
 */
export const EndCardAlpha: React.FC = () => (
  <AbsoluteFill>
    <TypeLayer />
  </AbsoluteFill>
);
