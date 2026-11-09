"""Split Mandarin answers in a transcript CSV into scoring words.

The test pages make one score button per space-separated piece of a trial's
answer (see AnnotatedAudio.options in static/record.js), so a Mandarin answer
must have a space between words. Answers typed with no spaces become one
button for the whole sentence, and answers with a space after every character
become one button per character. This program rewrites the answer column so
there is one button per word.

How a sentence is split:
  1. Existing spaces and Chinese/English punctuation are removed.
  2. jieba cuts the characters into words (dictionary only, no guessing of
     unknown words, so the same sentence always gives the same words).
  3. Grammatical particles (by default 的 地 得 了 吧 着 们) are joined to the
     word before them, the way the AzBio Mandarin lists are scored:
     很棒 的 -> 很棒的, 加班 了 -> 加班了.
  4. Words listed in --user_words are kept whole; --overrides fixes whole
     sentences by hand and always wins.

Answers that contain "/" (alternative answers) are never changed; they are
marked for review instead.

The output CSV keeps every other column byte for byte. A review CSV lists
each trial with the old and new answer, so a native speaker can check the
changes before the new file replaces the old one.

Check the method against lists that people already split by hand:
    python3 segment_mandarin.py --input metadata/azbio_mandarin_transcript.csv \
        --evaluate

Split a new list:
    python3 segment_mandarin.py --input mspsen_transcript.csv \
        --output mspsen_transcript_segmented.csv \
        --review mspsen_segmentation_review.csv
"""
import csv
import logging
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from absl import app, flags

DEFAULT_ATTACH = "的地得了吧着们"

# Punctuation that may appear in typed transcripts but is never scored.
PUNCTUATION = re.compile(
    r"[\s，。！？、；：“”‘’（）《》〈〉【】…—·,.!?;:\"'()\[\]]+")


def strip_text(answer: str) -> str:
    """Remove spaces and punctuation, leaving only the spoken characters."""
    return PUNCTUATION.sub("", answer)


def attach_particles(words: Sequence[str], attach: Set[str]) -> List[str]:
    """Join each particle in `attach` to the word before it."""
    out: List[str] = []
    for word in words:
        if out and word in attach:
            out[-1] += word
        else:
            out.append(word)
    return out


class Segmenter:
    """Cuts a string of Chinese characters into scoring words."""

    def __init__(self, attach: str = DEFAULT_ATTACH,
                 user_words: Iterable[str] = (),
                 overrides: Optional[Dict[str, str]] = None):
        import jieba  # imported here so the rest of the repo does not need it
        jieba.setLogLevel(logging.ERROR)
        self._tokenizer = jieba.Tokenizer()
        for word in user_words:
            word = word.strip()
            if word:
                # A high count makes jieba keep the word whole.
                self._tokenizer.add_word(word, freq=10**6)
        self.attach = set(attach)
        self.overrides = {
            strip_text(k): v.split() for k, v in (overrides or {}).items()}

    def words(self, answer: str) -> List[str]:
        text = strip_text(answer)
        if not text:
            return []
        if text in self.overrides:
            return list(self.overrides[text])
        cut = self._tokenizer.lcut(text, HMM=False)
        return attach_particles(cut, self.attach)


@dataclass
class Trial:
    line_number: int
    prefix: str        # everything before the answer, kept unchanged
    answer: str        # the answer as it is in the file
    ending: str        # the line ending, kept unchanged


def read_trials(path: str, num_fields: int) -> List[Trial]:
    """Read a transcript CSV the same way AudioDB.parse_csv does.

    Each line has `num_fields` comma-separated fields and the answer is the
    last one (it may itself contain commas).
    """
    trials = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        for i, line in enumerate(f, start=1):
            body = line.rstrip("\r\n")
            ending = line[len(body):]
            if not body.strip():
                trials.append(Trial(i, body, "", ending))
                continue
            parts = body.split(",", num_fields - 1)
            if len(parts) != num_fields:
                raise ValueError(
                    f"{path}:{i}: expected {num_fields} fields, found "
                    f"{len(parts)}: {body!r}")
            answer_field = parts[-1]
            answer = answer_field.strip()
            lead = answer_field[:len(answer_field) - len(answer_field.lstrip())]
            prefix = ",".join(parts[:-1]) + "," + lead
            trials.append(Trial(i, prefix, answer, ending))
    return trials


@dataclass
class Change:
    line_number: int
    old: str
    new: str
    status: str   # "unchanged", "changed", "check: ..." (needs a person)


def segment_trials(trials: Sequence[Trial], segmenter: Segmenter
                   ) -> List[Change]:
    changes = []
    for t in trials:
        if not t.answer:
            continue
        if "/" in t.answer:
            changes.append(Change(t.line_number, t.answer, t.answer,
                                  "check: has alternatives, left as is"))
            continue
        words = segmenter.words(t.answer)
        new = " ".join(words)
        if strip_text(new) != strip_text(t.answer):
            # Only possible with a bad override; never lose characters.
            changes.append(Change(t.line_number, t.answer, t.answer,
                                  "check: override changes the characters"))
            continue
        status = "unchanged" if new == t.answer else "changed"
        if any(len(w) >= 5 for w in words):
            status += "; check: long word"
        changes.append(Change(t.line_number, t.answer, new, status))
    return changes


def write_trials(path: str, trials: Sequence[Trial], changes: Sequence[Change]):
    new_answer = {c.line_number: c.new for c in changes}
    with open(path, "w", encoding="utf-8", newline="") as f:
        for t in trials:
            f.write(t.prefix + new_answer.get(t.line_number, t.answer)
                    + t.ending)


def write_review(path: str, changes: Sequence[Change]):
    with open(path, "w", encoding="utf-8", newline="") as f:
        out = csv.writer(f)
        out.writerow(["line", "status", "old_answer", "new_answer",
                      "old_words", "new_words"])
        for c in changes:
            out.writerow([c.line_number, c.status, c.old, c.new,
                          len(c.old.split()), len(c.new.split())])


def boundaries(words: Sequence[str]) -> Set[int]:
    """Character positions where one word ends and the next begins."""
    cuts, position = set(), 0
    for word in words[:-1]:
        position += len(word)
        cuts.add(position)
    return cuts


def agreement(pairs: Iterable[Tuple[Sequence[str], Sequence[str]]]
              ) -> Dict[str, float]:
    """Compare word boundaries of (reference, predicted) splits.

    Precision: share of predicted boundaries that the reference also has.
    Recall: share of reference boundaries that were predicted.
    Exact: share of sentences split exactly like the reference.
    """
    hits = predicted = expected = exact = total = 0
    for reference, guess in pairs:
        ref, pred = boundaries(reference), boundaries(guess)
        hits += len(ref & pred)
        predicted += len(pred)
        expected += len(ref)
        exact += list(reference) == list(guess)
        total += 1
    precision = hits / predicted if predicted else 1.0
    recall = hits / expected if expected else 1.0
    f1 = (2 * precision * recall / (precision + recall)
          if precision + recall else 0.0)
    return {"sentences": total, "precision": precision, "recall": recall,
            "f1": f1, "exact": exact / total if total else 1.0}


def read_overrides(path: Optional[str]) -> Dict[str, str]:
    """CSV with columns sentence,words: words is the split to use."""
    if not path:
        return {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        return {row["sentence"]: row["words"] for row in csv.DictReader(f)}


def read_user_words(path: Optional[str]) -> List[str]:
    if not path:
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.split()[0] for line in f
                if line.strip() and not line.startswith("#")]


FLAGS = flags.FLAGS
flags.DEFINE_string("input", None, "Transcript CSV to split.")
flags.DEFINE_string("output", None,
                    "Where to write the split CSV (never the input file).")
flags.DEFINE_string("review", None, "Where to write the review CSV.")
flags.DEFINE_integer("num_fields", 6,
                     "Comma-separated fields per line; the answer is last. "
                     "6 for AzBio lists, 7 for QuickSIN-style lists.")
flags.DEFINE_string("attach", DEFAULT_ATTACH,
                    "Particles joined to the word before them.")
flags.DEFINE_string("user_words", None,
                    "Text file, one word per line, never to be split.")
flags.DEFINE_string("overrides", None,
                    "CSV (sentence,words) of hand-made splits that win.")
flags.DEFINE_bool("evaluate", False,
                  "Compare the method with the spaces already in --input.")
flags.mark_flag_as_required("input")


def main(argv):
    del argv
    trials = read_trials(FLAGS.input, FLAGS.num_fields)
    segmenter = Segmenter(FLAGS.attach, read_user_words(FLAGS.user_words),
                          read_overrides(FLAGS.overrides))
    if FLAGS.evaluate:
        unique = {t.answer for t in trials if t.answer and "/" not in t.answer}
        scores = agreement((a.split(), segmenter.words(a)) for a in unique)
        print(f"{FLAGS.input}: {scores['sentences']} sentences, "
              f"boundary precision {scores['precision']:.3f}, "
              f"recall {scores['recall']:.3f}, F1 {scores['f1']:.3f}, "
              f"exactly the same {scores['exact']:.1%}")
        for a in sorted(unique):
            guess = " ".join(segmenter.words(a))
            if guess != a:
                print(f"  by hand: {a}\n  program: {guess}")
    changes = segment_trials(trials, segmenter)
    if FLAGS.output:
        if FLAGS.output == FLAGS.input:
            raise app.UsageError(
                "--output must differ from --input; check the review first.")
        write_trials(FLAGS.output, trials, changes)
    if FLAGS.review:
        write_review(FLAGS.review, changes)
    counts: Dict[str, int] = {}
    for c in changes:
        key = c.status.split(";")[0]
        counts[key] = counts.get(key, 0) + 1
    print(", ".join(f"{v} {k}" for k, v in sorted(counts.items())),
          f"(checks: {sum('check' in c.status for c in changes)})")


if __name__ == "__main__":
    app.run(main)
