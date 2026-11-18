# Peer review, tests: does the interface state one thing, and is it tested?

Course: Stanford University, EE292M, AI-Augmented R&D: Foundations and Practice, Fall 2026.
Form: ee292m_round4. Capstone review: yes. Written 2026-11-18 06:24 UTC by feedback_helper 147bfa0.

## Reviewer information

- SUNet ID: hanlinyu
- First name: Hanlin
- Last name: Yu

## Reviewee information

- SUNet ID: luyunqi
- First name: Yunqi
- Last name: Lu
- Repository: https://github.com/yunqilu/SpeechInNoise
- Reviewed commit: ba441e7 on main

## Environment

- date: Tue Nov 17 22:24:58 PST 2026
- whoami: yuhan
- uname -a: MINGW64_NT-10.0-26200 Ubcengin 3.5.4-395fda67.x86_64 2024-11-25 09:49 UTC x86_64 Msys
- repo path: build/SpeechInNoise-yunqilu

## Checklist

Score: 5 of 5

### 1. The author finished the sentence 'If they take away one thing, it should be ...', and the first screen is built around that one thing, with the rest cut or kept as backup.

Verified: yes

The one thing, in the author's words, and what was cut:

The central message is to make word-level speech-in-noise scoring faster and more consistent. We identified two users: raters who score spoken words, and lab members who prepare Mandarin transcript lists.

The scoring screen should emphasize keyboard shortcuts and word-level responses. Transcript segmentation and native-speaker review belong to the preparation workflow, not the rater's primary screen.

I suggested making the main takeaway explicit and separating completed, blocked, and upcoming work in the README. The current materials do not independently establish that the first screen has been fully reorganized around this message.

### 2. We have gone through the interface mark by mark: each color, line and number means one thing, one group of related items has its own color used everywhere, and unsettled parts are labeled as drafts.

Verified: yes

The group and its colors, what is marked as a draft, and any word borrowed from the audience:

We reviewed the scoring controls and Mandarin segmentation interface. A key problem is that the review CSV records statuses such as "changed", "unchanged", and "check: long word", but the generated scoring CSV is not clearly identified as an unreviewed draft.

I recommended using a `_draft` filename until native-speaker corrections are complete, so an unverified transcript cannot be mistaken for a final scoring list.

The five-character threshold for "check: long word" also needs an explanation. Interface colors and labels should be consistent, but the reviewed evidence does not establish that every visual mark already satisfies this requirement.

### 3. We have discussed what is tested and what should be, and for each of unit, integration, end-to-end and smoke I saw one test, or we agreed where the missing one belongs; we named one wrong program the tests would still pass, and one tripwire any error would move.

Verified: yes

One test of each kind, or where the missing one belongs; the wrong program, and the tripwire:

We discussed the existing tests and the missing coverage at each level.

Unit: The Mandarin segmenter's word-splitting rules and particle-attachment behavior should be checked, including whether changing `--attach` changes the result as expected.

Integration: The existing `test_unsplit_and_character_split_answers_give_the_same_words` is an important regression test because the same spoken answer must produce consistent scoring words. A further test should compare sentences shared across MSPSEN and BKB-SIN, once both real lists are available.

End-to-end: A browser test should verify that keyboard scoring produces the same recorded answers as mouse scoring. Smoke: A minimal scoring workflow should confirm that the page loads and a trial can be completed.

One wrong program that could still pass the existing tests would split the same sentence differently across two lists, changing the number of scoring buttons and potentially the scores.

A useful tripwire is a regression test that fails whenever a frozen `metadata/*_transcript.csv` changes unexpectedly, together with cross-list word-consistency checks. Missing tests are proposed, not claimed as already implemented.

### 4. We have discussed which tests save the author time, and what in this project no test can see, and I understood both.

Verified: yes

The tests that pay for themselves, and the scope no test covers:

The most valuable tests are those preventing silent changes in word-level scoring. The existing equivalence test for unsplit and character-split answers protects the central scoring behavior and saves repeated manual regression checks.

Additional tests for shared sentences, particle-attachment settings, and frozen transcripts would further reduce the risk of changing established scoring results when preparing new Mandarin lists.

However, automated tests cannot determine whether a Mandarin sentence has been linguistically segmented correctly. The existing hand-segmented AzBio references contain inconsistent conventions, so agreement or F1 scores against them are not absolute ground truth. Native-speaker review remains essential.

Tests also do not establish whether keyboard shortcuts actually make raters faster. A timed comparison of mouse-based and keyboard-based scoring sessions would be needed to support that usability claim.

### 5. We have discussed at least one suggestion I made on how this code could be improved.

Verified: yes

State the suggestion and what was decided:

My main suggestion was to clearly distinguish automatically generated Mandarin scoring lists from native-speaker-approved lists.

The splitter already produces a review CSV with statuses such as "changed", "unchanged", and "check: long word", but the output scoring CSV is not clearly marked as a draft. This creates a risk that an unreviewed list could be uploaded and used to score participants before its word boundaries are approved.

I recommended using a `_draft.csv` filename until the native-speaker review and manual overrides are complete, then promoting the reviewed list to its final filename. I also suggested documenting the five-character threshold used to flag unusually long words.

We discussed this as a practical improvement to the transcript-preparation workflow. The reviewed commit does not establish that draft labeling has already been implemented; that should remain a follow-up rather than be reported as completed work.

## Attestation

Completed: 5 of 5 checklist items.

All of my answers are true and accurate to the best of my understanding and ability, and I will upload this feedback to the reviewee's repository and verify that it was uploaded.

Signed: Hanlin Yu
