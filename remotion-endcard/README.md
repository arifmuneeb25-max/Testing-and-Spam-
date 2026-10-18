# EndCard

A 5 second kinetic typography end card. 1920 x 1080, 24 fps, 120 frames.
Every animated value is derived from the current frame with `interpolate()` and
`Easing`, so two renders of the same frame are byte for byte the same image.
There is no CSS transition, keyframe or timer anywhere in the project.

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

`EndCardAlpha` is the same type on the same timeline with no plate, no black
fade and no grain, on a transparent background, for compositing over the plate
in an edit.

## Where things live

| File | What it holds |
| --- | --- |
| `src/theme.ts` | Every number: colours, positions, start frames, durations |
| `src/components/Word.tsx` | The standard 10 frame reveal, and the drift "stop." uses |
| `src/components/Ghost.tsx` | One failure stacked behind "lose" |
| `src/components/Grain.tsx` | Per frame deterministic monochrome noise |
| `src/TypeLayer.tsx` | Eyebrow, both lines, the ghost layer. Shared by both compositions |
| `src/EndCard.tsx` | Plate, black fade, type, grain |
| `src/EndCardAlpha.tsx` | Type only, transparent |

Retiming is a `theme.ts` edit. Nothing else carries a frame number.

## Two calls worth knowing about

**Ghost fade length.** The brief asks for a 14 frame fade on each of the three
ghosts. Ghost 3 starts on frame 31, so 4 rise + 4 hold + 14 fall leaves it alive
until frame 53, which is the first frame of the held beat where nothing is
allowed to move. The fade is derived from `GHOSTS_END` (frame 50) instead, which
keeps the 4 frame rise and 4 frame hold exact and gives falls of 15, 13 and 11.
Move `GHOSTS_END` to change it.

**Trailing letter space.** CSS puts the letter spacing after the last glyph too,
which throws a centred line off centre by half of it. Every word carries a
matching negative right margin so the lines centre on the true glyph run.
