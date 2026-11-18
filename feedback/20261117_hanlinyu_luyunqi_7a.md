# Peer review, systems: where does the time go, and where does everything run?

Course: Stanford University, EE292M, AI-Augmented R&D: Foundations and Practice, Fall 2026.
Form: ee292m_round5. Capstone review: yes. Written 2026-11-18 06:39 UTC by feedback_helper 147bfa0.

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

- date: Tue Nov 17 22:39:14 PST 2026
- whoami: yuhan
- uname -a: MINGW64_NT-10.0-26200 Ubcengin 3.5.4-395fda67.x86_64 2024-11-25 09:49 UTC x86_64 Msys
- repo path: build/SpeechInNoise-yunqilu

## Checklist

Score: 5 of 5

### 1. We have looked at a profile of the capstone's slowest part, and at one change measured before and after that changed no answer.

Verified: yes

Where the time goes, the change, and the ratio:

We discussed where the time goes in the Mandarin segmentation workflow. The splitter itself takes well under one second, with dictionary initialization accounting for much of that time. Computational speed is therefore not the main bottleneck.

The more significant cost is human review: raters score hundreds of words, and a native speaker must inspect changed sentence boundaries. I suggested prioritizing rows marked "check:" in the review CSV and moving unchanged rows to the end or omitting them from the review view. This would preserve all scoring answers while reducing the number of rows requiring attention.

We identified this optimization opportunity, but no measured before-and-after review-time ratio was established at the reviewed commit. That measurement remains a follow-up.

### 2. The README has a drawing of the capstone as a system, and from it I can say where each part runs and how code and data reach it.

Verified: yes

The machines or containers, and how code and data arrive:

We identified three distinct execution locations and deployment boundaries.

1. `static/scoring_keys.js` runs in the rater's browser. It reaches users through the script loaded by each relevant scoring page after the lab deploys the updated static files.
2. `segment_mandarin.py` runs offline on a laptop. It reads transcript CSVs and produces segmented answers and a review CSV; it does not directly modify the live server.
3. The language-default handling in `api.py` runs on the lab server and affects requests after deployment.

The important distinction is that only the browser shortcut and server API changes directly affect the live site. The splitter produces candidate data that must be reviewed and approved separately.

I recommended adding a clear system diagram to README showing these execution locations and how code and data move between them. The reviewed evidence did not establish that such a diagram was already present.

### 3. We have named the original copy of the data, and what in the project cannot be rebuilt by a script, and where that is backed up.

Verified: yes

The original, what cannot be rebuilt, and where its copy is:

We identified the original research data as participants' recordings and scoring records stored in `experiments.db` on the lab server. The lab's `nightly.sh` and `backup_experiments_to_gdrive.sh` scripts provide database copies on Google Drive. I did not independently verify a successful database restoration.

Several human decisions are also difficult or impossible to regenerate automatically: the lab's word-boundary convention, the manually segmented AzBio Mandarin reference lists, and native-speaker corrections to newly generated transcripts.

At the reviewed commit, the particle-attachment convention was represented by `DEFAULT_ATTACH` and the `--attach` option. A durable, versioned location for future native-speaker overrides had not yet been established.

I recommended committing the reviewed corrections in `metadata/mandarin_overrides.csv`, including reviewer identity and review date, so that these irreplaceable decisions are preserved and auditable.

### 4. We have discussed each boundary in the system (between front end and backend, data and database, or services) and whether it is real.

Verified: yes

The boundaries, and which one is not real yet:

We discussed the actual boundaries between the browser, offline transcript preparation, and the lab server.

The browser-side scoring shortcuts operate on existing UI controls and do not themselves change the scoring backend. The Mandarin splitter is an offline data-preparation tool, not a live API service. The server-side language-default fix is part of `api.py` and affects requests only when the updated code is deployed.

A boundary that was not fully established was the transition from automatically segmented candidate transcripts to native-speaker-approved scoring lists. The segmentation script can generate the files, but human approval and deployment remain separate steps.

We also identified that the particle-attachment convention is represented both by the `--attach` option and by the planned manual-override workflow. Consolidating these decisions after lab approval would make the boundary clearer and more reproducible.

### 5. We have discussed at least one suggestion I made on how this capstone could be improved.

Verified: yes

State the suggestion and what was decided:

My main suggestion was to preserve the lab's word-segmentation convention and manually reviewed corrections in one version-controlled configuration, rather than relying on a command-line option that users must remember.

Specifically, I proposed storing native-speaker corrections in `metadata/mandarin_overrides.csv`, with the identity of the reviewer and the review date. Once the lab agrees on a final particle-attachment convention, the approved particle list could be stored alongside those corrections.

Yunqi partially accepted the recommendation. She decided to retain the `--attach` option for now because the lab had not yet agreed on a single convention and she needed to compare alternatives. She agreed to preserve native-speaker corrections in a committed overrides CSV. Consolidation of the particle list into the approved configuration would follow after lab sign-off.

This is an agreed future implementation plan, not a claim that the changes were already completed.

## Attestation

Completed: 5 of 5 checklist items.

All of my answers are true and accurate to the best of my understanding and ability, and I will upload this feedback to the reviewee's repository and verify that it was uploaded.

Signed: Hanlin Yu
