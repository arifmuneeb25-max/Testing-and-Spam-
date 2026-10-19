# EndCard

A 5 second kinetic typography end card. 1920 x 1080, 24 fps, 120 frames.
Every animated value is derived from the current frame with `interpolate()` and
`Easing`, so two renders of the same frame are the same image. There is no CSS
transition, keyframe or timer anywhere in the project.

## The plate

Put `endcard_plate.png` in `public/`.

The file already there is the stage floor reference at 1672 x 941. Swap in the
true 1920 x 1080 plate before the final render, otherwise the 1.04 settle is
upscaling a smaller image and the floor goes soft.

## Running it

```
npm install
npm run dev     # Remotion Studio
```

## Render

```
npx remotion render EndCard out/endcard.mp4 --codec=h264 --crf=16
npx remotion render EndCardAlpha out/endcard_alpha.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le
```

`EndCardAlpha` is the text, ghosts and scrim on the same timeline with no
plate, no plate dim, no black fade and no grain, on a transparent background,
for compositing over the plate in an edit.

## Where things live

| File | What it holds |
| --- | --- |
| `src/theme.ts` | Every number: colours, positions, start frames, durations |
| `src/components/Word.tsx` | The standard 10 frame reveal, and the drift "stop." uses |
| `src/components/Ghost.tsx` | One failure stacked behind "lose" |
| `src/components/Scrim.tsx` | The soft navy pool the type sits in |
| `src/components/Grain.tsx` | Per frame deterministic monochrome noise |
| `src/TypeLayer.tsx` | Scrim, ghosts and all three lines. Shared by both compositions |
| `src/EndCard.tsx` | Plate, dim, type, black fade, grain |
| `src/EndCardAlpha.tsx` | Type layer only, transparent |

Retiming is a `theme.ts` edit. Nothing else carries a frame number.

## How readability is handled

Three things stack, because no one of them is enough over a lit floor with
confetti on it:

1. The plate dims to 0.62 brightness between frames 8 and 24.
2. A radial navy scrim, 1500 x 620, fades in over the same frames. It reaches
   zero alpha well inside the frame, so there is no edge and no band.
3. Every word carries a dark navy halo. The plate has a pool of light in the
   middle of it, so a light glow would do nothing.

## One conflict in the brief

The brief asks for the block to be centred vertically, and also gives line
centres of 420, 526 and 670. Those do not agree. Measured on a render, the ink
runs y 384 to 735, so its centre sits at 559.5, about 20px below the centre of
the frame. The explicit numbers won, since they are the more specific
instruction.

To centre the ink instead, take 20px off each of `line1Y`, `line2Y` and
`line3Y` in `src/theme.ts`.

Line centres are line box centres, which is why the measured ink centre of each
line sits a little above it: these lines are mostly cap height with few
descenders, and `stop.` has a deep one.
