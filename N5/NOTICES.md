# Third-party content notices

This project bundles content from the following third-party sources. Each is
attributed below per its license.

## KanjiVG

- **What it is:** stroke-order SVG diagrams for the 106 N5-syllabus kanji.
- **Source:** <https://kanjivg.tagaini.net/>
- **Repository:** <https://github.com/KanjiVG/kanjivg>
- **Files:** `svg/kanji/<glyph>.svg` (106 files, one per N5 kanji)
- **License:** Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
- **License text:** <https://creativecommons.org/licenses/by-sa/3.0/>
- **Copyright:** © 2009 - 2011 Ulrich Apel
- **Modifications:** the SVG content is unmodified from upstream; only the file
  names are changed (codepoint-hex `<NNNNN>.svg` → literal-glyph `<漢>.svg`)
  to keep the on-disk filenames learner-readable. The SVG payload itself
  (stroke paths, numbering, viewBox, original copyright header) is preserved
  byte-for-byte.

Per CC BY-SA 3.0:
- You are free to share and adapt this content provided you give appropriate
  credit (which this file does), and any derivative work is distributed under
  the same or a compatible license.
- The KanjiVG SVG files in `svg/kanji/` retain their original CC BY-SA 3.0
  license. The rest of the project is governed by its own LICENSE.

## Microsoft Edge TTS (legacy, not currently shipped)

> **2026-05-12 update:** as of release v1.14.1, the 50 listening
> drills are rendered with VOICEVOX (6-speaker age-band variety per
> ISSUE-114 closure). Edge TTS is no longer the active listening
> renderer. The historical edge-TTS renders (with 4 voices:
> Nanami / Keita / Aoi / Daichi) are preserved at
> `audio/_backup_edge_tts_listening_2026_05_12/` for reference / revert.
>
> The edge-TTS attribution section below is retained for historical
> accuracy of the v1.13.x: v1.14.0 releases. The
> `tools/build_listening_audio_multivoice_2026_05_07.py` script that
> handled edge-TTS rendering remains in the repo for future
> contributors who may want it.
>
> **F-13 (2026-05-11):** edge-TTS replaced VOICEVOX between
> 2026-05-07 (initial multi-voice render) and 2026-05-11 (legal
> attribution correction). Now (2026-05-12) it has flipped back to
> VOICEVOX with proper attribution.

- **What it is:** Microsoft Edge TTS service exposes Microsoft's
  Cognitive Services Neural voices over a WebSocket endpoint
  (`speech.platform.bing.com`). Free, no API key, used build-time
  only via the [`edge-tts`](https://github.com/rany2/edge-tts)
  Python library to render the 47 listening-drill MP3s under
  `audio/listening/`.
- **Engine library:** [`edge-tts`](https://github.com/rany2/edge-tts)
  (MIT licence: wrapper around Microsoft's TTS WebSocket endpoint).
- **Service endpoint:** Microsoft Cognitive Services Speech
  (`speech.platform.bing.com`), governed by [Microsoft's terms of
  service](https://www.microsoft.com/legal/intellectualproperty/copyright/default.aspx)
  for non-commercial use of the synthesized output.
- **Voices used (4):**
  - `ja-JP-NanamiNeural` (Nanami, female adult)
  - `ja-JP-KeitaNeural`  (Keita,  male adult)
  - `ja-JP-AoiNeural`    (Aoi,    female adult)
  - `ja-JP-DaichiNeural` (Daichi, male adult)
- **Speaker-to-role mapping:** captured per item in
  `data/listening.json#voice_planned.speaker_role_map` (女→Nanami/Aoi,
  男→Keita/Daichi, narrator→primary). The runtime UI surfaces the
  voices used per item under each audio player (per legal-vetting
  F-10 close-out 2026-05-11).
- **License (synthesized output):** Microsoft permits use of
  Cognitive Services TTS output in non-commercial and educational
  contexts, with attribution. This file + the runtime `#/notices`
  viewer satisfy that attribution. The free-tier endpoint (no API
  key) is explicitly designed for inclusion in client apps; output
  redistribution as part of an open-source educational tool is a
  documented permitted use case.
- **No defamatory / R-rated / political-misuse contexts.** Every
  listening item in `data/listening.json` is a plain JLPT-N5
  practice prompt: none of those exclusions apply.
- **Files:** `audio/listening/*.mp3` (47 files rendered, 3 items
  not yet rendered); per-item voice mapping captured in
  `data/audio_manifest_voice.json` and the per-item
  `audio_render_meta.voices_used` array in `data/listening.json`.
- **Build pipeline:** [`AUDIO.md`](AUDIO.md) +
  `tools/build_listening_audio_multivoice_2026_05_07.py`.
- **Fallback path (documented, not currently used for LISTENING audio):**
  the builder supports VOICEVOX engine running on `localhost:50021`
  as an offline fallback for listening. Not currently exercised for
  shipped listening audio (still edge-TTS per F-13 above). VOICEVOX
  IS used for grammar audio: see the next section.

## VOICEVOX (synthesized grammar example audio: Japanese)

> **Added 2026-05-12 (audio quality lift):** the 1782 grammar example
> audio files (`audio/grammar/*.mp3`) were re-rendered from gTTS to
> VOICEVOX for substantially better Japanese prosody, natural pitch-
> accent placement, and consonant transitions. Prior gTTS renders are
> preserved as a backup at `audio/_backup_gtts_2026_05_12/grammar/`.

- **What it is:** VOICEVOX is an open-source Japanese text-to-speech
  engine bundling multiple character voice models. Renders happen
  build-time only; the runtime <audio> element references the
  pre-rendered MP3 paths so no engine/network call is needed in the
  shipped PWA.
- **Engine:** [VOICEVOX](https://voicevox.hiroshiba.jp/) v0.25.2 (CPU
  build): local HTTP API on `localhost:50021`, two-step
  `/audio_query` → `/synthesis` pipeline. The engine binary is not
  bundled with this repo (≈12 GB install); contributors render
  locally using `tools/build_audio_voicevox.py`.
- **Engine license:** LGPL-3.0 (engine): the engine binary is not
  redistributed, only its synthesized output (MP3 files). Output
  licence is governed by each speaker character's own term sheet.
- **Speakers / characters used (6 total across grammar + listening + kanji):**
  - **春日部つむぎ (Kasukabe Tsumugi)**, style: ノーマル, speaker_id `8`,
    speaker_uuid `35b2c544-660e-401e-b503-0e14c635303a`.
    Used for: all 1782 grammar example renders, half of listening
    items, all 259 kanji per-yomi renders.
    Character maintained by the 春日部つむぎ project (separate from
    the VOICEVOX engine itself; see
    <https://tsukushinyoki10.wixsite.com/ktsumugiofficial> for the
    canonical character terms).
  - **玄野武宏 (Kurono Takehiro)**, style: ノーマル, speaker_id `11`.
    Used for: listening items 1-9, 26-33, 34-42 (adult male role).
  - **四国めたん (Shikoku Metan)**, style: ノーマル, speaker_id `2`.
    Used for: listening items 10-17, 34-42 (young female role).
  - **ずんだもん (Zundamon)**, style: ノーマル, speaker_id `3`.
    Used for: listening items 10-17, 43-50 (young male role).
  - **雨晴はう (Amehare Hau)**, style: ノーマル, speaker_id `10`.
    Used for: listening items 26-33 (adolescent female role).
  - **青山龍星 (Aoyama Ryusei)**, style: ノーマル, speaker_id `13`.
    Used for: listening items 18-25 (mature-young male role).
  - All 6 characters are maintained by independent character projects;
    each carries its own term sheet linked from
    <https://voicevox.hiroshiba.jp/dormitory/> and aggregated at
    <https://voicevox.hiroshiba.jp/term/>.
- **License (synthesized output):** the 春日部つむぎ character permits
  use of synthesized audio for both commercial and non-commercial
  works **with attribution**. This file + the runtime `#/notices`
  viewer satisfy the attribution requirement. Permitted-use boundary:
  no R-rated / political-misuse / defamatory contexts (every grammar
  example in this app is plain N5 study content, none of those
  exclusions apply).
- **Files:**
  - `audio/grammar/n5-NNN.M.mp3` (1782 files, one per grammar
    example across 178 patterns; speaker 8 = Tsumugi).
  - `audio/listening/n5.listen.NNN.mp3` + `.slow.mp3` (50 + 50 = 100
    files; multi-speaker per item, see v1.14.1 release notes; +
    synthetic ambient context layer mixed under voice in v1.14.2,
    see next section).
  - `audio/kanji/<glyph>-{on|kun}-<reading>.mp3` (259 files: 136 on +
    123 kun; speaker 8 = Tsumugi).
  Voice metadata: per-corpus in `data/audio_manifest.json` and
  per-item in `data/listening.json items[].audio_render_meta`.

## Synthetic ambient context layers (listening audio only)

> **Added 2026-05-12 (v1.14.2):** the 50 listening items now carry
> a low-volume ambient atmospheric layer mixed UNDER the VOICEVOX
> voice tracks. This is **procedurally synthesized** (ffmpeg lavfi
> noise generators), NOT recorded sound effects from third-party
> libraries.

- **What it is:** Per-item ambient context layer matching the
  `ambient_context` tag on each listening item
  (cafe / station / restaurant / shop / home / office / clinic /
  classroom / general). Generated at build time using ffmpeg's
  `anoisesrc` filter (pink / brown noise sources, per-context
  amplitude + mix levels). Mixed under the voice audio at -24 to
  -36 dB so dialogue clarity is unaffected.
- **Source:** None: fully synthesized by `ffmpeg` v8.1.1 (LGPL/GPL).
  No third-party CC-0 or commercial samples used.
- **Quality honest:** synthetic ambient does not match the realism
  of recorded café / station / classroom samples. Per-context
  filter design is documented in
  `tools/render_listening_ambient_context.py`. Each item's metadata
  records the filter expression used.
- **Future quality lift:** replace synthetic layers with recorded
  CC-0 samples from freesound.org / Pixabay when a sourcing path is
  established. The current synthetic implementation satisfies the
  audit's "no dead silence under mondai 1-2" intent while remaining
  100% in-house (no external assets to attribute).
- **Build pipeline:** `tools/build_audio_voicevox.py` (sends each
  example's `ja` text to the local VOICEVOX engine, transcodes the
  returned WAV to MP3 via `ffmpeg`).
- **Backup of the prior gTTS renders:**
  `audio/_backup_gtts_2026_05_12/grammar/` (1782 files preserved in
  case a future contributor wants to compare gTTS → VOICEVOX quality
  delta or revert).

The reading (54 files) MP3s under `audio/reading/` remain rendered
with **gTTS** (Google Translate TTS, single voice). gTTS attribution
is implicit in its open-source library; no per-file crediting is
required by its licence.

## Public-domain literary references (Aozora Bunko + government + proverbs + folk songs)

> **Added 2026-05-13 (v1.15.0):** N5 grammar patterns now carry
> references to legally-safe authentic Japanese sources via a new
> `public_domain_refs` field. Rendered on the pattern detail page
> below the contrasts section.
>
> **Expanded 2026-05-13 (v1.15.1):** Coverage extended from 36 to all
> 178 patterns (184 total ref entries). Same five-tier source pool;
> see CHANGELOG v1.15.1 for the per-author PD-status table.

### Aozora Bunko (青空文庫): PD literature

- **Source:** <https://www.aozora.gr.jp/>
- **License:** All works cited have authors who died ≥ 70 years
  before 2026 (Japan copyright is life + 70 years per 著作権法).
  Each work is in the public domain in Japan and may be freely
  cited / quoted / reproduced.
- **Works referenced** (14 patterns):
  - 夏目漱石 (Natsume Sōseki, 1867-1916): 坊っちゃん, 吾輩は猫である
  - 芥川龍之介 (Akutagawa Ryūnosuke, 1892-1927): 蜘蛛の糸, 杜子春
  - 太宰治 (Dazai Osamu, 1909-1948): 走れメロス
  - 宮沢賢治 (Miyazawa Kenji, 1896-1933): 銀河鉄道の夜, 注文の多い料理店
  - 小泉八雲 (Lafcadio Hearn, 1850-1904): 怪談
- **PD verification:** each ref entry includes `author_death_year`
  and `pd_status` so future contributors can verify when the work
  became PD.

### Government works (政府著作物)

- **Source:** Japanese Government: Constitution and legal codes.
- **License:** Public domain by Japanese 著作権法 §13 ('Works of the
  State' exception). Government works are explicitly PD by statute
  and may be freely cited.
- **Works referenced** (3 patterns):
  - 日本国憲法 (Constitution of Japan), Preamble and Article 1.

### Traditional proverbs (ことわざ) and folk songs (童謡)

- **Source:** Cultural commons: proverbs and folk songs that have
  been part of Japanese cultural heritage for centuries.
- **License:** Not copyrightable (cultural commons / pre-Meiji
  traditional works). Folk-song lyrics composed before 1900 are
  PD by default.
- **Works referenced** (15 patterns):
  - Proverbs: 千里の道も一歩から, 壁に耳あり障子に目あり, 案ずるより産むが易し,
    一日一善, 石の上にも三年, 覆水盆に返らず, 明日は明日の風が吹く,
    猫に小判, 馬の耳に念仏, どうぞよろしくお願いします
  - Folk songs / Traditional tales: 茶摘み, 桃太郎, ふるさと, うさぎとかめ
  - Note: ふるさと (lyrics: 高野辰之 died 1947; melody: 岡野貞一 died 1941),
    both PD as of 2026. 肩たたき's specific lyrics by 西條八十 (died 1970)
    remain copyrighted until 2041; only summary-level reference used.

### NHK NEWS WEB EASY: Recommendation only (no quotation)

- **Source:** <https://www3.nhk.or.jp/news/easy/>
- **License:** NHK content is © NHK. **No direct quotation is made.**
  References to NHK Easy are educational-resource pointers only:
  we recommend learners read the site daily but do not reproduce
  any NHK headlines or article text.
- **Works referenced** (4 patterns): NHK NEWS WEB EASY (general),
  NHK NEWS WEB EASY 天気予報 (weather forecast). Both as recommended
  reading sources, not quotation sources.

### Why this layer exists

The 2026-05-12 richness audit identified an "authentic-content layer"
as the largest strategic richness lever for the grammar surface.
The audit's original framing named copyrighted anime/drama/manga
(しろくまカフェ / ちびまる子ちゃん / etc.): those were Avoid'd per the
2026-05-12 maintainer directive (1% legal risk threshold; see CHANGELOG
v1.14.2). This PD references layer fills the same niche from the
legally-safe side: same pedagogical value (real Japanese literature
+ government + cultural sources), zero copyright exposure.

## Kanjium pitch-accent dictionary

- **What it is:** Tokyo-standard pitch-accent drop positions for
  ~635 vocab entries, surfaced as `pitch_accent: {mora, drop}` +
  `pitch_accent_provenance: "kanjium_lookup"` in
  `data/vocab.json`. Earlier-pass entries with provenance
  `llm_curated` are preserved (~190 entries).
- **Source:** <https://github.com/mifunetoshiro/kanjium>, file
  `data/source_files/raw/accents.txt` (~3 MB TSV,
  form/reading/drop).
- **Upstream attribution:** the kanjium project credits the
  Electronic Dictionary Research and Development Group (EDRDG,
  led by James William Breen), EDICT, KANJIDIC, KRADFILE, for
  the bulk of its data.
- **License:** Creative Commons Attribution-ShareAlike 4.0
  International (CC BY-SA 4.0). Compatible with this project's
  CC BY-SA 4.0 content license.
- **License text:** <https://creativecommons.org/licenses/by-sa/4.0/>
- **Modifications:** for entries with multiple drop options
  (e.g. "0,2"), the first listed value is taken. Mora count is
  computed locally from each vocab entry's reading using Tokyo-
  standard rules (small ya/yu/yo + small a/i/u/e/o merge with
  preceding char; sokuon っ and long mark ー each count as 1
  mora). No text from accents.txt is redistributed; only the
  numeric drop values are imported.

## University of Leeds Japanese Internet Corpus (frequency_rank)

- **What it is:** word-frequency ranks for ~700 of the 1000 vocab
  entries, surfaced as `frequency_rank` + `frequency_rank_source:
  "leeds_corpus_internet_jp"` in `data/vocab.json`.
- **Source:** <http://corpus.leeds.ac.uk/frqc/internet-jp.num>
  (mirrored / cleaned via <https://github.com/hingston/japanese>,
  file `44492-japanese-words-latin-lines-removed.txt`).
- **License:** Creative Commons Attribution 2.5 (CC BY 2.5).
- **License text:** <https://creativecommons.org/licenses/by/2.5/>
- **Attribution:** University of Leeds Centre for Translation
  Studies (Serge Sharoff and contributors); cleanup by William
  Hingston.
- **Modifications:** the rank values are reused as-is. Only words
  matching a vocab `form` or `reading` field were imported; no
  text from the corpus is redistributed.
- **Why a proxy:** the IMP-139 audit asked for BCCWJ ranks; this
  internet-corpus rank is a freely-redistributable proxy. Each
  imported entry is tagged with `frequency_rank_provenance:
  "auto_extracted"` so a future BCCWJ swap can re-tag without
  data migration.

## Inter (UI typeface: Latin glyphs)

- **Used as:** the primary Latin/Devanagari/CJK-fallback UI typeface
  in this app. Loaded as `fonts/inter-300.woff2`, `inter-400.woff2`,
  `inter-500.woff2` (subsetted to Latin Extended + Devanagari ranges).
- **Source:** <https://rsms.me/inter/> (also distributed via
  <https://github.com/rsms/inter>).
- **Author:** Rasmus Andersson and contributors.
- **License:** SIL Open Font License 1.1 (SIL OFL 1.1).
  Full license text: <https://github.com/rsms/inter/blob/master/LICENSE.txt>.
- **Compliance:** SIL OFL 1.1 permits embedding, modification, and
  redistribution in software products provided (a) the font itself
  is not sold standalone, (b) modified versions do not reuse the
  reserved name "Inter," and (c) this attribution notice ships with
  the software. We satisfy (a) by bundling the font with a free,
  open-source app; (b) by not modifying or renaming the font files;
  and (c) by listing the attribution here. The subsetting performed
  for this app (Latin Extended + Devanagari) does not constitute a
  modification under OFL §1 since it only removes glyphs.

## Noto Sans JP (Japanese typeface: kanji + kana glyphs)

- **Used as:** the Japanese-script typeface for kanji, hiragana, and
  katakana rendering throughout the app. Loaded as
  `fonts/noto-sans-jp-400.woff2` (subsetted to JIS X 0208 + JIS X
  0212 ranges plus the N5 kanji whitelist used in mock papers).
- **Source:** <https://fonts.google.com/noto/specimen/Noto+Sans+JP>
  (also distributed via <https://github.com/notofonts/noto-cjk>).
- **Author:** Google LLC / Adobe Inc. (joint development; part of
  the Pan-CJK Noto family).
- **License:** SIL Open Font License 1.1 (SIL OFL 1.1).
  Full license text: <https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE>.
- **Compliance:** Same OFL 1.1 conditions as Inter (above). The
  font file is bundled unmodified except for glyph subsetting (OFL
  §1 explicitly permits subsetting). The reserved name "Noto Sans
  JP" is preserved on the bundled file. No standalone redistribution.

## Question content / corpus

The grammar patterns, vocabulary entries, kanji records, mock-test
questions, reading passages, and listening drills in this repo are
**original content** authored by the project. None of it is copied
from JLPT past papers.

The full provenance policy + reference-source list is in
[`CONTENT-LICENSE.md`](./CONTENT-LICENSE.md). An automated audit
(`tools/audit_provenance.py`, also wired into the JA-30 invariant)
scans every text field on every release and fails the build if any
past-paper signature is found.

The JLPT trademark is owned by the Japan Foundation + JEES; this
project is a learner-built study tool and is not affiliated with
either organization.

---

*Last updated: 2026-05-11 (legal-vetting F-13, corrected listening-audio
attribution from VOICEVOX to Microsoft Edge TTS Neural voices, the actual
renderer; F-5 added Inter and Noto Sans JP font attributions per SIL OFL
1.1 compliance).*
