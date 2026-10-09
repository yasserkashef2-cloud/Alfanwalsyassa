# QA summary — what was actually tested
Environment: headless Chromium (Playwright) on Linux, opened via file:// . No Safari/Firefox/real mobile device.

**Passed (automated):**
- Structure: 5 units, 17 items, 32 views; every item has 5 vocabulary sections, 6 questions, 2 comparative prompts.
- 551 internal links and 504 paragraph/time reference buttons resolve; 0 broken.
- 0 JavaScript errors; 0 broken images; local fonts load; no horizontal overflow on any page at 1280px and 390px.
- Reading titles render rgb(138,28,28); listening titles rgb(15,63,145) on all 17 items.
- Interactions: card flip, star, font size, reading mode, answers saved and restored after reload, completion checkbox and progress bar, paragraph jump, download answers, TOC drawer + Esc, video button builds the YouTube iframe, timestamp chip re-points it with start=, cloze feedback, vocabulary search (Arabic and English), self-assessment saved.
- ألبوم مصر iframe: 18 cards render; the connectors page has no iframe and its button opens assets/legacy/arabic-connectors.html with target=_blank (link present; new-tab loading itself not clicked through).
- Accessibility smoke test: alt text, button names, textarea/select labels, iframe titles, one h1 per view, lang=ar dir=rtl; tab order checked on the cover only.
- Print: A4 PDF generation works (9 pages for one item).
- Source fidelity: all 276 text blocks are exact substrings of attachment.txt; every non-empty source line is present.
- Can-Do quotes: 86 statements compared with the PDFs; 70 matched verbatim by column; the other 16 are split across columns in the PDF and were matched at page level or by reading.
- In-text highlighting (readings only): 90 of 102 glossary entries highlighted (automatic matching; first occurrence only).

**Not verified:** actual YouTube playback (no access to YouTube from the test machine; file:// may trigger error 153); Arabic fonts of the original Word files; screen-reader behaviour; Safari/Firefox/iOS/Android; print layout beyond one page set; correctness of every vocabulary diacritic/gloss; whether embedded legacy pages behave offline beyond what rendered here.
