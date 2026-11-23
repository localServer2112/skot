# Home hero background video

`site/pages/index.html` expects two files here:

    hero.mp4    H.264 / AAC-less (audio stripped), the baseline source
    hero.webm   VP9, served first to browsers that take it

Requirements
- Silent. The element is `muted loop playsinline autoplay`; any audio track is dead weight.
- ~8–15s, cut to loop seamlessly.
- 1920x1080 or wider, 16:9 or wider — the card crops with `object-fit:cover`.
- Keep each file under ~4 MB. It loads on first paint.
- Shoot/grade for a dark overlay: the scrim in `.vhero-scrim` sits on top at
  roughly 70% ink, so low-contrast, mid-tone footage reads best.

Until the files exist the hero falls back to `assets/img/hero-voice.jpg`
(set both as the `poster` attribute and as the card's CSS background), which is
also what is shown under `prefers-reduced-motion: reduce`.

Encoding, once ffmpeg is available:

    ffmpeg -i source.mov -an -t 12 -vf scale=1920:-2 -c:v libx264 -crf 24 -preset slow -movflags +faststart hero.mp4
    ffmpeg -i source.mov -an -t 12 -vf scale=1920:-2 -c:v libvpx-vp9 -crf 34 -b:v 0 hero.webm

## Current file

`hero.mp4` is "Woman Talking While Holding a Microphone" by Pavel Danilyuk,
https://www.pexels.com/video/woman-talking-while-holding-a-microphone-8716788/
(Pexels licence: free for commercial use, attribution not required). It is the
1280x720 rendition (4.0 MB); the 1920x1080 one is 9.7 MB. There is no `hero.webm`,
so the page lists only the mp4 source. Swap it by replacing the file.
