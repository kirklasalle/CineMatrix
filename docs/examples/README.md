# Storyboard AI — Master Example Scripts Suite

Welcome to the official **Storyboard AI Example Scripts Suite**. This directory contains **27 world-class sample scripts** designed to demonstrate every parser, visual art style, cinematic engine, audio scoring tool, and export feature provided by Storyboard AI.

---

## Interactive Quickstart Guide

To test any example script:
1. Open the Storyboard AI Web Studio at `http://localhost:5173`.
2. Click **Create Project** or navigate to **Script Upload**.
3. Drag & drop any file from `docs/examples/` (or select via file browser).
4. Select your preferred **Art Style** and **Target Engine**.
5. Click **Generate Storyboard** to initiate multi-modal AI analysis.

---

## 1. Ingestion Formats (`docs/examples/formats/`)

This suite verifies all 8 supported file formats and automatic format detection.

| File | Format | Genre / Setting | Scenes | Features Tested |
| :--- | :--- | :--- | :--- | :--- |
| [`01_screenplay_hollywood.fountain`](file:///d:/Projects/storyboard/docs/examples/formats/01_screenplay_hollywood.fountain) | `.fountain` | Heist Thriller | 3 | Dual dialogue, parentheticals, transitions, title metadata |
| [`02_final_draft_noir.fdx`](file:///d:/Projects/storyboard/docs/examples/formats/02_final_draft_noir.fdx) | `.fdx` (Final Draft) | 1940s Film Noir | 2 | Native FDX XML tags, scene properties, character voiceover |
| [`03_television_drama.docx`](file:///d:/Projects/storyboard/docs/examples/formats/03_television_drama.docx) | `.docx` (MS Word) | Political Thriller | 2 | Bold scene headers, centered character cues, act structure |
| [`04_feature_thriller.pdf`](file:///d:/Projects/storyboard/docs/examples/formats/04_feature_thriller.pdf) | `.pdf` (Screenplay) | Submarine Action | 1 | Standard Courier 12pt margins, PDF text extraction |
| [`05_av_commercial_doc.txt`](file:///d:/Projects/storyboard/docs/examples/formats/05_av_commercial_doc.txt) | Two-Column `.txt` | Ocean Documentary | 4 | Two-column audio/visual timing, voiceover & music cues |
| [`06_stage_play_broadway.txt`](file:///d:/Projects/storyboard/docs/examples/formats/06_stage_play_broadway.txt) | Stage Play `.txt` | Victorian Drama | 2 | ACT/SCENE numbering, bracketed stage directions, dialogue |
| [`07_comic_book_issue.cbz`](file:///d:/Projects/storyboard/docs/examples/formats/07_comic_book_issue.cbz) | `.cbz` (Comic ZIP) | Cyberpunk Action | 2 | Sequential page artwork, `ComicInfo.xml`, panel descriptions |
| [`08_novel_chapter_prose.epub`](file:///d:/Projects/storyboard/docs/examples/formats/08_novel_chapter_prose.epub) | `.epub` (eBook) | Sci-Fi Space Opera | 1 | Narrative prose chunking, chapter detection, dialogue parsing |
| [`09_standard_screenplay.txt`](file:///d:/Projects/storyboard/docs/examples/formats/09_standard_screenplay.txt) | Plain Text `.txt` | Cold War Espionage | 1 | Universal INT./EXT. headers, character slugs, action lines |

---

## 2. Flagship AI Engines (`docs/examples/engines/`)

Specialized scripts crafted to showcase our deep cinematic analysis algorithms.

| File | Target Engine | Key Demonstrations | Recommended Style |
| :--- | :--- | :--- | :--- |
| [`10_story_doctor_15_beats.fountain`](file:///d:/Projects/storyboard/docs/examples/engines/10_story_doctor_15_beats.fountain) | **Story Doctor** | Complete Blake Snyder 15-Beat Sheet structure, narrative tension curve, executive coverage report | `oscar_prestige` |
| [`11_table_read_ensemble_cast.fountain`](file:///d:/Projects/storyboard/docs/examples/engines/11_table_read_ensemble_cast.fountain) | **Table Read Studio** | 6-character vocal ensemble mapped to `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` voice models | `film_noir` |
| [`12_action_animatic_motion.fountain`](file:///d:/Projects/storyboard/docs/examples/engines/12_action_animatic_motion.fountain) | **Video & Motion Engine** | 6 camera motion presets (`dolly_in`, `dolly_out`, `pan_left`, `pan_right`, `handheld`, `slow_motion`) | `concept_art_digital` |
| [`13_graphic_novel_manga_studio.fountain`](file:///d:/Projects/storyboard/docs/examples/engines/13_graphic_novel_manga_studio.fountain) | **Graphic Novel Studio** | 4-Quadrant, 6-Grid, Dynamic Action, Manga Split panel layouts, 300 DPI print PDF export | `manga_kinetic` |
| [`14_cinematic_audio_score_foley.fountain`](file:///d:/Projects/storyboard/docs/examples/engines/14_cinematic_audio_score_foley.fountain) | **Audio Scoring & Foley** | Procedural soundtrack synthesis (`cinematic_epic`, `horror_ambient`) & procedural foley cues (`cinematic_boom`, `door_slam`) | `expressionist_horror` |
| [`15_character_archetypes_lookbook.fountain`](file:///d:/Projects/storyboard/docs/examples/engines/15_character_archetypes_lookbook.fountain) | **Character Look-Book** | 8 Jungian archetypes (Hero, Sage, Rebel, Shadow, Mentor, Trickster, Caregiver, Sovereign) | `golden_age_hollywood` |

---

## 3. Cinematic Genres & Art Styles (`docs/examples/genres/`)

Showcases the harmony between the **Style Vault (16 Styles)** and the **Genre Vault (18 Genres)**.

| File | Genre | Art Style | Visual Characteristics |
| :--- | :--- | :--- | :--- |
| [`16_sci_fi_cyberpunk_neo_noir.fountain`](file:///d:/Projects/storyboard/docs/examples/genres/16_sci_fi_cyberpunk_neo_noir.fountain) | Sci-Fi / Cyberpunk | `neo_noir_neon` | Wet streets, neon cyan/amber split, Blade Runner aesthetic |
| [`17_historical_prestige_drama.fountain`](file:///d:/Projects/storyboard/docs/examples/genres/17_historical_prestige_drama.fountain) | Historical Drama | `oscar_prestige` | Deakins natural candlelight, Rembrandt chiaroscuro, rich depth |
| [`18_horror_psychological_dread.fountain`](file:///d:/Projects/storyboard/docs/examples/genres/18_horror_psychological_dread.fountain) | Psychological Horror | `expressionist_horror` | Caligari distorted geometry, elongated shadows, Nosferatu angles |
| [`19_action_blockbuster_kinetic.fountain`](file:///d:/Projects/storyboard/docs/examples/genres/19_action_blockbuster_kinetic.fountain) | Action Heist | `comic_book` | Kirby energy, bold ink lines, Ben-Day dot shading, dynamic speed |
| [`20_whimsical_comedy_symmetry.fountain`](file:///d:/Projects/storyboard/docs/examples/genres/20_whimsical_comedy_symmetry.fountain) | Whimsical Comedy | `wes_anderson` | Strict bilateral symmetry, pastel mustard/mint palette, deadpan center |
| [`21_romantic_impressionist_memory.fountain`](file:///d:/Projects/storyboard/docs/examples/genres/21_romantic_impressionist_memory.fountain) | Romance Drama | `wong_kar_wai` | Step-printed motion blur, Christopher Doyle lens flare impressionism |
| [`22_gritty_documentary_verite.txt`](file:///d:/Projects/storyboard/docs/examples/genres/22_gritty_documentary_verite.txt) | Cinema Verité | `dogme_naturalist` | Available light only, handheld camera shake, raw unvarnished truth |
| [`23_animation_fantasy_fairytale.fountain`](file:///d:/Projects/storyboard/docs/examples/genres/23_animation_fantasy_fairytale.fountain) | Anime / Fantasy | `anime_cinematic` | Studio Ghibli painterly warmth, atmospheric haze, character appeal |
| [`24_spaghetti_western_standoff.fountain`](file:///d:/Projects/storyboard/docs/examples/genres/24_spaghetti_western_standoff.fountain) | Spaghetti Western | `classic_pencil` | Sergio Leone 3-way extreme close-ups, dust, high-noon contrast |

---

## 4. Duration Spectrum Benchmarks (`docs/examples/spectrum/`)

Calibrated benchmark tiers for rapid prototyping through full pilot production testing.

| File | Tier | Duration | Scenes | Target Use Case |
| :--- | :--- | :--- | :--- | :--- |
| [`25_micro_scene_1min.fountain`](file:///d:/Projects/storyboard/docs/examples/spectrum/25_micro_scene_1min.fountain) | Micro Pitch | 1 Minute | 1 | Rapid 10-second end-to-end generation & provider connectivity verification |
| [`26_short_film_5min.fountain`](file:///d:/Projects/storyboard/docs/examples/spectrum/26_short_film_5min.fountain) | Short Film | 5 Minutes | 5 | Standard 3-act mini-arc for evaluating pacing, character consistency, and PDF deck export |
| [`27_tv_pilot_teaser_10min.fountain`](file:///d:/Projects/storyboard/docs/examples/spectrum/27_tv_pilot_teaser_10min.fountain) | TV Pilot Teaser | 10 Minutes | 10 | Enterprise multi-plot benchmark testing full animatic reels, shot-list CSV, and CBZ comic bundles |
