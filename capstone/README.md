# Can the Mandarin speech-in-noise tests be scored fast and the same way every time?

**What it is for, and for whom.** For the audiologists and researchers in Stanford's
STAR Lab who test how well people understand speech in noise, in English and now in
Mandarin. A listener hears a sentence in noise and repeats it; a person, or a speech
recognizer, scores each word right or wrong. That score is only as good as the list
of "words" behind it. In the lab's web app today, the MSPSEN lists show each Mandarin
sentence as one unbroken string (one button for the whole sentence) and the BKB-SIN
lists split it into single characters (one button per character), so the same
listener gets a different score depending on the list. Scoring is also all clicks,
and nobody has checked how well the recognizer scores Mandarin. This project fixes
the scoring units, makes manual scoring fast, and measures the recognizer, so that
the lab can compare L1 Chinese / L2 English listeners with L1 English / L2 Chinese
listeners on equal terms.

**Current state.**

- Keyboard scoring works on every test page and on the rater page: number keys flip
  words 1 to 12, `A`/`N` all/none, `Space` play, `Enter` next once every word is
  scored. 9 browser tests.
- `segment_mandarin.py` splits answers into scoring words. Against the hand-split
  AzBio Mandarin lists (40 sentences), word-boundary F1 is 0.935 (precision 0.944,
  recall 0.926); 50 % of sentences match exactly. The disagreements are of two kinds:
  the hand split is not consistent with itself (很高兴 is one word, but 不 规则的 is
  two), and the program makes real mistakes (期限得 加班了, where 得 means "must" and
  is not a particle; 这 周 轮 到 instead of 这周 轮到). So the tool proposes and a
  native speaker confirms, through a review CSV. 13 tests.
- Found and fixed a bug: choosing "Default" on the start page gave a 400 error on
  the Spanish and Mandarin tests (wrong language code). 5 tests.
- Not done yet: the MSPSEN and BKB-SIN lists are not in the GitHub repository (only
  AzBio Mandarin is), so they cannot be re-split until we get them from the server.

EE292M capstone. The plan for the agent is in [PROMPT.md](PROMPT.md); this file is
for reviewers.

## Where things are

The repository is a fork of the lab's
[SpeechInNoise](https://github.com/MalcolmSlaney/SpeechInNoise). The lab is writing a
paper from this code and needs `main` to stay traceable, so every change is a
separate branch that becomes one pull request to the lab:

| Branch | What it changes |
| --- | --- |
| `scoring-keyboard-shortcuts` | `static/scoring_keys.js`, one `<script>` line per page, `scoring_keys_test.py` |
| `mandarin-word-segmentation` | `segment_mandarin.py`, `segment_mandarin_test.py`, `jieba` in requirements |
| `mandarin-default-language` | `api.py` (`PROJECT_LANGUAGES`), `api_language_test.py` |
| `capstone` | all of the above merged, plus this folder |

## Running it

```bash
pip install -r requirements.txt          # jieba is the only new package
pytest --ignore=asr_test.py --ignore=offline_asr_test.py \
       --ignore=offline_asr_whisper_test.py   # the ASR tests need torch/whisper

# Keyboard tests run in a real browser; they skip themselves without Playwright.
pip install playwright && playwright install chromium
pytest scoring_keys_test.py

# How close is automatic splitting to the hand-split AzBio lists?
python3 segment_mandarin.py --input metadata/azbio_mandarin_transcript.csv --evaluate

# Split a new list; read the review CSV before it replaces anything.
python3 segment_mandarin.py --input mspsen_transcript.csv \
    --output mspsen_split.csv --review mspsen_review.csv
```

To try the shortcuts by hand without the server: `python3 -m http.server -d static`,
open `azbio_mandarin.html`, and in the browser console run
`audio.options("我 知道 一家 很棒的 小店")`.

## Top risks

1. **The MSPSEN and BKB-SIN lists live only on the server**, not in GitHub. Asked the
   lab where they are; until then the splitter is tested on AzBio Mandarin.
2. **What counts as one word is a lab decision**, not a program's. The splitter
   follows the AzBio convention (particles such as 的/了/吧 stay with the word before
   them); the lab has to agree before any list is changed, and a native speaker
   checks every changed sentence.
3. **Changing a list changes the scores.** Re-split lists should be uploaded as new
   lists, with old results kept as they were, so the paper's numbers stay traceable.
