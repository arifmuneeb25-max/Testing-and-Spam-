import React from 'react';
import {AbsoluteFill} from 'remotion';
import {TypeLayer} from './TypeLayer';

/**
 * Same type, same timing, nothing behind it. Renders with a transparent
 * background so the card can be built over the plate in an edit instead.
 */
export const EndCardAlpha: React.FC = () => (
  <AbsoluteFill>
    <TypeLayer />
  </AbsoluteFill>
);
