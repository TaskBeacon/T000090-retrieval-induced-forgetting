# Retrieval-Induced Forgetting

| Metadata | Value |
|---|---|
| Name | Retrieval-Induced Forgetting |
| Version | 0.1.0 |
| Date Updated | 2026-08-23 |
| PsyFlow Version | 0.1.0 |
| PsychoPy Version | 2025.1.1 |
| Modality | Behavioral / keyboard text entry |
| Language | Chinese |
| Task ID | `T000090` |
| Slug | `retrieval-induced-forgetting` |
| Variant | `baseline` |
| TAPS Contract | `v0.2.0` |

## 1. Task Overview

This task implements the classic retrieval-practice paradigm. Participants learn
taxonomic category-exemplar pairs, repeatedly retrieve half of the exemplars from
half of the categories, complete a filled retention interval, and finally recall
all studied items. Final-test performance is separated into practiced items
(`Rp+`), unpracticed competitors from practiced categories (`Rp-`), and baseline
items from unpracticed categories (`Nrp`). Retrieval-induced forgetting is
quantified as `Nrp accuracy - Rp- accuracy`.

| Field | Value |
|---|---|
| Task ID | T000090 |
| Slug | retrieval-induced-forgetting |
| Primary construct | Adaptive forgetting / retrieval inhibition |
| Response modality | Typed cued recall; F/J parity judgment |
| Human duration | Approximately 35-45 minutes |
| Canonical runtime | PsyFlow / PsychoPy |

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

1. Study 48 category-exemplar pairs (8 categories × 6 exemplars).
2. Practice 12 Rp+ items from 4 categories, repeated three times.
3. Complete 120 fixed 10-second arithmetic parity trials (20-minute filled interval).
4. Recall all 48 items from category-plus-first-character cues.

### Trial-Level Flow

| Stage | Visible content | Duration / response |
|---|---|---|
| Study | Category name above intact exemplar | 5 s, no response |
| Retrieval practice | Category, first-character stem, editable field | Type word; Return; 10 s maximum |
| Distractor | Addition equation, F-odd and J-even choices | Fixed 10 s |
| Final test | Category, first-character stem, editable field | Type word; Return; 7 s maximum |

### Controller Logic

No adaptive controller is used. A participant-seeded planner fixes all category
assignments, Rp statuses, practice repetitions, and final-test ordering before
the first trial. Rp-/Nrp cues precede Rp+ cues to reduce output interference.

### Other logic

All typed responses are Unicode-normalized and compared exactly with the planned
Chinese exemplar. Static participant-facing wording and the complete item bank
live in configuration files rather than task code.

## 3. Configuration Summary

### a. Subject Info

| Setting | Value |
|---|---|
| Subject ID | Three digits (101-999) |
| Window | 1280 × 720 px, white background |
| Font | SimHei |
| Fullscreen | Disabled by default |

### b. Window Settings

The task uses a 1280 × 720 pixel window, white background, and SimHei text.

### c. Stimuli

Study screens show one category-exemplar pair. Practice and final-test screens
show a category, first-character stem, and editable response box. Distractor
screens show a concrete addition equation with spatial odd/even options.

### d. Timing

| Parameter | Human value | Evidence status |
|---|---:|---|
| Categories × items | 8 × 6 | Direct |
| Practiced categories × items | 4 × 3 | Direct |
| Practice repetitions | 3 | Direct |
| Study duration | 5 s | Direct |
| Practice response window | 10 s | Direct |
| Filled retention interval | 20 min | Adapted content, direct duration |
| Final-test response window | 7 s | Direct |

### Triggers

Trigger codes distinguish experiment/phase lifecycle, study and practice onsets,
each final-test item status, text submission, distractor choices, and timeouts.
The default human driver uses a loopback serial URL and can be replaced through
the structured `triggers.driver` configuration.

### QA and simulation

- `config/config_qa.yaml`: short four-category mechanism-complete visual QA.
- `config/config_scripted_sim.yaml`: deterministic responder smoke simulation.
- `config/config_sampler_sim.yaml`: task-specific sampler with probabilistic parity accuracy.

Run locally:

```powershell
python main.py human --config config/config.yaml
python main.py qa --config config/config_qa.yaml
python main.py sim --config config/config_scripted_sim.yaml
python main.py sim --config config/config_sampler_sim.yaml
```

## 4. Methods (for academic publication)

Participants studied 48 Chinese category-exemplar pairs drawn from eight
taxonomic categories. Four categories were selected by a participant-seeded
counterbalancing procedure. Three of six exemplars from each selected category
were assigned to repeated retrieval practice (Rp+); the remaining exemplars in
those categories were Rp-, and all exemplars in unselected categories were Nrp.
Each intact pair appeared for 5 s. Rp+ items were then retrieved three times from
a category-plus-first-character stem with a 10-s response window. Participants
completed a 20-min filled interval comprising 120 fixed-duration arithmetic
parity judgments. The final test presented category-plus-first-character cues
for all studied items with a 7-s typed-response window. Critical Rp- and Nrp
items were tested before Rp+ items. The primary RIF index was the difference
between Nrp and Rp- final-test accuracy; retrieval facilitation was the
difference between Rp+ and Nrp accuracy.

The phase structure and primary parameters follow Anderson, Bjork, and Bjork
(1994, 2000). The Chinese word translations and parity distractor content are
documented adaptations; Wimber et al. (2015) supports the adaptive-forgetting
construct and competing-memory suppression account. See `references/` for the
paper bundle, parameter mapping, stimulus mapping, and logic audit.
