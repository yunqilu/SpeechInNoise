Make the Mandarin speech-in-noise tests in the STAR Lab web app (this repository)
score the same way every time, fast, by person or by recognizer, so the lab can
compare L1 Chinese / L2 English listeners with L1 English / L2 Chinese listeners.

# 1 Context

The app plays a sentence in noise, the listener repeats it, and each word of the
answer gets a button that a person marks right or wrong (`AnnotatedAudio.options` in
`static/record.js`; the rater page builds the same buttons in
`static/review_modules/annotations.js`). The buttons come from splitting the answer
column of `metadata/<project>_transcript.csv` on spaces. A recognizer (`asr.py`,
`offline_asr.py`) also transcribes each reply and is scored against the same answer,
with `/` marking alternatives and `homonym_list.csv` listing words that sound alike.

Problems, as seen on the live site (quicksin.stanford.edu/jnd/):

- MSPSEN answers have no spaces: one button per sentence.
- BKB-SIN answers have a space after every character: one button per character.
- Scoring is mouse-only; a session has hundreds of words.
- Nobody has measured how well the recognizer scores Mandarin.

Terms. **Scoring word**: one button, scored right or wrong. **Particle**: a
grammatical character such as 的 地 得 了 吧 着 们 that the AzBio Mandarin lists
attach to the word before it (很棒的, 加班了). **L1/L2**: native / second language.

# 2 Rules

- Never commit to `main` or change the lab's `main`. One branch per change, each a
  pull request the lab can review alone; `capstone` merges them.
- Never change an existing transcript in place. A re-split list is a new file, so
  results already in the database keep the answer they were scored against.
- No audio, databases, subject data or secrets in the repository.
- Every change comes with tests that run under plain `pytest` (browser tests skip
  themselves without Playwright).

# 3 Milestones

**M1 (done).** Keyboard scoring (`static/scoring_keys.js`); the splitter
(`segment_mandarin.py`, boundary F1 0.935 against hand-split AzBio Mandarin); the
"Default" list fix for Spanish and Mandarin (`api.py`).

**M2. Re-split MSPSEN and BKB-SIN.** Get both transcript CSVs from the lab. Run the
splitter with `--review`; a native speaker checks every changed sentence and records
fixes in an overrides CSV; re-run until the review is clean. Add them as new
projects in `projects.py` and `api.py`, the way AzBio Mandarin is added. Check:
the same sentence gives the same words in both lists; no characters are lost
(the splitter refuses that already).

**M3. Measure the recognizer on Mandarin.** For each Mandarin trial with both a
person's score and a recognizer transcript, compare word by word. Output a CSV (one
row per trial: answer, recognizer text, person's marks, recognizer's marks) and the
agreement per subject and SNR. Check whether recognizer errors come from splitting
(the recognizer's words cut differently from the answer's) rather than hearing:
score both on characters and on scoring words.

**M4. Support the L1/L2 comparison.** For each subject, the score per test and SNR in
one CSV, with language group (L1 Chinese / L1 English) as a column, so the two groups
can be compared directly.

# 4 Top risks

1. The MSPSEN and BKB-SIN lists are not in GitHub. Fallback: keep developing on AzBio
   Mandarin, which has the same format.
2. The word convention is a lab decision. The splitter makes it a setting
   (`--attach`), not a hard-coded rule.
3. The recognizer's output may not be reachable from outside the server. Fallback: an
   export from the database, run offline.
