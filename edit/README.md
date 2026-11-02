# 7SKIN 7S-06 — skrip edit

Klip sumber: folder Google Drive "Stand" (c01–c14 ikut urutan upload).

- `music.py`: generate background music (house lembut 118 BPM, tiada copyright)
- `sfx.py`: bunyi pop/whoosh untuk teks
- `render.py`: potong setiap babak (satu take terbaik bagi setiap ayat), colour grade, teks Fredoka
- `mix.py`: cantum babak + music auto-duck bawah suara + SFX, loudness -14 LUFS

## Larissa Kisslock Bag (15s)

- `larissa.py`: 7 cuts from RAW "2/11 Handbag larissa", white Inter Bold overlays (fade + slide up),
  original colours (no filter), original audio, no background music. Output `LARISSA_kisslock_preview_15s.mp4`.

## Larissa Kisslock Bag — 6 video set

`python3 edit/sfx2.py WORK/sfx && python3 edit/videos.py RAWDIR WORK larissa`
(RAWDIR holds `hb.mov` = talking raw, `r1.mov`/`r2.mov` = silent B-roll.)

- `engine.py`: cuts, full-frame B-roll cutaways, pop-in photo stickers, white text (fade + slide), synthesised SFX.
  No colour filter (range-correct scaling only), no background music.
- `videos.py`: T1-T3 talking (voice matched to B-roll), O1-O3 overlay only.
