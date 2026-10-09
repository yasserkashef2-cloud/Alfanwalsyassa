# الفن والسياسة — Art and Politics
Interactive virtual book for advanced learners of Arabic. Prepared and curated by Yasser Kashef.
© 2026 Yasser Kashef. All rights reserved. Design carried out by AI.

## How to open
1. Unzip the whole folder (do not move `index.html` out of it — it needs `assets/`).
2. Double-click `index.html` (any current Chrome / Edge / Firefox / Safari). No server, no install.
3. Optional, recommended for video: from inside the folder run `python3 -m http.server 8000`, then open http://localhost:8000

## Does it need the internet?
- Works offline: all text, vocabulary, questions, fonts (self-hosted, OFL), images, the ألبوم مصر page, most tools/exercises.
- Needs internet: YouTube playback (7 videos; each also has a direct link that opens YouTube in a new tab). The 408-connectors page (`assets/legacy/arabic-connectors.html`) opens in a new tab and asks for Google Fonts, falling back to local fonts offline.
- Known limitation: YouTube may refuse to play inside a page opened straight from disk (`file://`, "error 153"). Use the direct link under each video or the local server above.
- Progress, answers, self-assessments and starred words are stored in your browser's localStorage only (nothing is sent anywhere).

## Folder
- `index.html` — the whole book (data inline)
- `assets/css`, `assets/js` — stylesheet and script
- `assets/fonts` — Amiri, Noto Naskh Arabic, Cairo, Source Serif 4 (SIL OFL 1.1, via @fontsource)
- `assets/img` — cover and five unit posters (JPG + WebP)
- `assets/legacy` — the two supplied HTML pages, unmodified
- `_generator/` — Python scripts and JSON data used to build the book (`python3 build.py`)
- `SOURCES_REPORT.md`, `QA_SUMMARY.md` — reports

## Units (17 items)
1 Music: R1, L1, R2, L2 · 2 Graffiti: R1, L1, R2 · 3 Jewelry: R1, L1 · 4 Comics: R1, L1, R2, L2 · 5 Cinema: R1, L1, R2, R3
(Gaps in the pattern come from the supplied materials — see SOURCES_REPORT.md.)
