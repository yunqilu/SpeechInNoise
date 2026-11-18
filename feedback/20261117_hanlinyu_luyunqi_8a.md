# Peer review, safety nets: where does the capstone stand, what does the agent know, and what catches a wrong result?

Course: Stanford University, EE292M, AI-Augmented R&D: Foundations and Practice, Fall 2026.
Form: ee292m_round6. Capstone review: yes. Written 2026-11-18 06:56 UTC by feedback_helper 147bfa0.

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

- date: Tue Nov 17 22:56:00 PST 2026
- whoami: yuhan
- uname -a: MINGW64_NT-10.0-26200 Ubcengin 3.5.4-395fda67.x86_64 2024-11-25 09:49 UTC x86_64 Msys
- repo path: build/SpeechInNoise-yunqilu

## Checklist

Score: 5 of 5

### 1. We have gone through the capstone check-in, docs/check-in.md, together, against the capstone plan: what works, what failed, what is cut, and one part to throw away and one to keep.

Verified: yes

What works, what failed, what is cut, and what the plan still claims:

We reviewed the capstone check-in against the original plan at commit `0796293`. The project has implemented keyboard-based word scoring and Mandarin segmentation, while Milestones 3 and 4 have been cut with reasons.

The intended final claim is specific: scoring should use consistent word boundaries across lists, those boundaries should be checked by a native speaker, and existing transcripts and scores should remain unchanged.

An important limitation is that 203 of 232 sentences require changes, and native-speaker review had not started at the reviewed version. I suggested defining what the November 30 draft could honestly claim if only part of the review was completed, for example distinguishing an approved MSPSEN list from a proposed BKB-SIN list.

The review also identified the value of keeping the frozen-transcript checks while treating unapproved segmentation outputs as provisional. The reviewed materials do not independently establish a complete failed-experiment account or an explicit throwaway/keep pair.

### 2. We have gone through what changed in the capstone's CLAUDE.md this week together (git log -p CLAUDE.md), and why: each line added is something the agent could not have found by reading the code, and each line cut has a reason.

Verified: yes

A line added and why it is needed, and a line cut and why:

At the reviewed commit, there was no `CLAUDE.md`, so there were no actual additions or removals to inspect this week.

We discussed several project-specific rules that should be added because they protect information or decisions an agent might otherwise overlook.

First, `.gitignore` matches `*.csv`, so a new transcript CSV may require explicit tracking with `git add -f`. Second, `metadata/transcripts.sha256` is a frozen reference and must not be modified without authorization. Third, changes should be developed on a branch based on the lab's current `main`, with one focused change per branch.

I recommended writing these instructions in a concise `CLAUDE.md` and testing their effect through fresh sessions with and without the instructions. These were proposed additions, not completed changes at the reviewed commit.

### 3. We have discussed which skill the author used this week and why; or, if none was used, why not, and which repeated procedure should become a skill.

Verified: yes

The skill and why it ran; or why none, and which skill to write:

No reusable skill had been executed at the reviewed commit. We discussed which repeated procedure would benefit most from becoming a skill.

My recommendation was a "before a pull request" verification skill because the project repeatedly submits changes to the lab repository.

The skill should start from the latest lab `main`, install the required test dependencies such as jieba and Playwright, run the relevant tests without treating skipped tests as passes, check that documented test counts match actual results, and list all files modified by the proposed PR.

This is motivated by inconsistent documented test counts, including 13 versus 15 and 85 versus 112 in the reviewed materials. A reusable skill would make verification more consistent and reduce the chance of submitting incomplete changes.

The procedure should be committed under `.claude/skills/` and tested in a fresh session before claiming it works.

### 4. We have named the safety nets of this capstone: the layers that would catch a wrong result (tests, a check against a known answer, a person's review, ...), one failure that would slip past all of them, and where the copies of the code and data are, one of them offline.

Verified: yes

The layers, the failure that slips past them, and where the copies are:

We discussed the project's existing safety nets: frozen-transcript regression checks, rejecting manual overrides that change the original characters, and native-speaker review of changed Mandarin word boundaries.

One important blind spot is that `.gitignore` excludes CSV files. A newly generated transcript can exist and pass tests locally but be absent from GitHub and the lab's checkout.

Another blind spot is that a transcript and its SHA-256 reference can be changed together, potentially defeating the frozen-data check unless the diff is reviewed independently.

The lab's `experiments.db` contains original participant results and is copied to Google Drive through backup scripts. However, a file copied while SQLite is being written may not be a consistent snapshot, and a successful restoration had not been demonstrated.

The reviewed materials identified server and Google Drive copies of the database, but no verified offline copy. The newly segmented lists and review CSV were stored only on a laptop outside the repository, making native-speaker corrections particularly vulnerable to loss.

These are acknowledged limitations rather than completed backup protections.

### 5. We have discussed at least one suggestion I made on how this capstone could be improved.

Verified: yes

State the suggestion and what was decided:

My main suggestion was to preserve the Mandarin segmentation outputs and native-speaker review decisions somewhere independent of Yunqi's laptop, with controlled lab access.

Specifically, I recommended storing the MSPSEN and BKB-SIN segmented lists and the review CSV in the lab's private Google Drive, alongside the existing research backups, and documenting their location in README.

I also recommended adding two rules to `CLAUDE.md`: never modify `metadata/transcripts.sha256` without explicit authorization, and explicitly track new CSV files because the repository's `.gitignore` excludes them.

Yunqi accepted the recommendation in our discussion. The agreed plan was to request a suitable lab Drive folder from Emily and preserve the three files before native-speaker review begins, then add the protective instructions to `CLAUDE.md`.

A pre-commit check preventing simultaneous changes to a transcript and its frozen checksum was left as a possible later improvement. These are agreed actions, not claims that implementation was already complete.

## Attestation

Completed: 5 of 5 checklist items.

All of my answers are true and accurate to the best of my understanding and ability, and I will upload this feedback to the reviewee's repository and verify that it was uploaded.

Signed: Hanlin Yu
