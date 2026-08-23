# Task Logic Audit

## 1. Paradigm Intent

- Task: Retrieval-Induced Forgetting (RIF), classic retrieval-practice paradigm.
- Primary construct: adaptive forgetting of competing memories after selective retrieval.
- Manipulated factors: item status at final test (`rp_plus`, `rp_minus`, `nrp`); selective retrieval practice versus no retrieval practice at category and item levels.
- Dependent measures: exact cued-recall accuracy and response time for each final-test item; facilitation (`Rp+ - Nrp`) and RIF (`Nrp - Rp-`) scores.
- Key citations: Anderson, Bjork, and Bjork (1994; W2043527309); Anderson, Bjork, and Bjork (2000; W2054727733); Wimber et al. (2015; W1977249777).

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: one session composed of four ordered phase blocks: study, retrieval practice, distractor, and final test.
- Trials per block (human): 48 study presentations; 36 retrieval-practice cues (12 Rp+ items repeated three times); 120 fixed-duration arithmetic distractor trials; 48 final cued-recall trials.
- Randomization/counterbalancing: a participant-seeded planner assigns four of eight categories to retrieval practice and three of six items within each practiced category to Rp+. The remaining practiced-category items become Rp- and items in unpracticed categories become Nrp. Study and practice orders are seeded and shuffled. Final-test order places Rp- and matched Nrp items before Rp+ items to reduce output interference, with seeded shuffling within tiers.
- Condition weight policy: not applicable. Exact cross-phase item identities and repetition counts cannot be represented by independent scalar label weights.
- Condition generation method: custom `generate_rif_session_plan(...)` in `src/utils.py`. Built-in label scheduling is insufficient because study, practice, and final-test trials must share the same category-item identities and counterbalanced Rp status. The generator returns phase-specific hashable `TrialPlan` values carrying immutable fields (`stage`, `condition_id`, `category`, `exemplar`, `cue`, `item_status`, repetition/test order, and distractor problem fields).
- Runtime-generated trial values: none in `run_trial.py`. All core factors, item assignments, cue strings, and arithmetic problems are generated before execution from `overall_seed` plus a stable participant-derived seed.

### Trial State Machine

1. Study item:
   - Onset trigger: `study_onset`.
   - Stimuli shown: category name above one intact exemplar, centered with explicit vertical separation.
   - Valid keys: none.
   - Timeout behavior: advances after 5 seconds.
   - Next state: next planned study item or practice instructions.
2. Retrieval-practice item:
   - Onset trigger: `practice_onset`.
   - Stimuli shown: category name, first-character exemplar stem, and an editable response field.
   - Valid keys: typed Chinese text; Return submits.
   - Timeout behavior: records blank/partial text as incorrect after 10 seconds.
   - Next state: next planned practice cue or distractor instructions.
3. Distractor item:
   - Onset trigger: `distractor_onset`.
   - Stimuli shown: a concrete arithmetic expression and two spatial response labels (F=odd, J=even).
   - Valid keys: `f`, `j`.
   - Timeout behavior: records no response; the screen remains for the configured fixed duration.
   - Next state: next arithmetic problem or final-test instructions.
4. Final-test item:
   - Onset trigger: `final_test_onset`.
   - Stimuli shown: category name, first-character stem, and an editable response field.
   - Valid keys: typed Chinese text; Return submits.
   - Timeout behavior: records blank/partial text as incorrect after 7 seconds.
   - Next state: next final-test item or summary.

## 3. Condition Semantics

- Condition ID: `rp_plus`.
  - Participant-facing meaning: an item from a practiced category that was itself repeatedly retrieved.
  - Concrete stimulus realization: intact category-exemplar pair at study, category-plus-first-character cue during three practice repetitions, and category-plus-first-character cue at final test.
  - Outcome rules: exact normalized typed response equals the exemplar.
- Condition ID: `rp_minus`.
  - Participant-facing meaning: an unpracticed competitor from a category whose other members were repeatedly retrieved.
  - Concrete stimulus realization: intact pair at study and category-plus-first-character cue only at final test.
  - Outcome rules: exact normalized typed response equals the exemplar.
- Condition ID: `nrp`.
  - Participant-facing meaning: an item from a category receiving no retrieval practice.
  - Concrete stimulus realization: intact pair at study and category-plus-first-character cue only at final test.
  - Outcome rules: exact normalized typed response equals the exemplar.
- Participant-facing text source: all static instructions, response labels, screen templates, and item-bank content are defined in `config/*.yaml`; `run_trial.py` only formats those config templates with planned values.
- Localization strategy: language variants replace config item banks and text without code edits. The baseline uses Chinese translations of taxonomic category-exemplar materials and SimHei.

## 4. Response and Scoring Rules

- Response mapping: Return submits typed practice/test responses; F means odd and J means even during the distractor.
- Response key source: `task.submit_key` and `task.distractor_keys` in config.
- Missing-response policy: timed-out text trials are incorrect; distractor timeouts are logged and do not alter the session plan.
- Correctness logic: practice/final responses are Unicode-normalized, trimmed, and compared exactly with the planned exemplar; distractor responses are compared with preplanned parity.
- Reward/penalty updates: none.
- Running metrics: final-test accuracy by Rp+, Rp-, and Nrp; facilitation = Rp+ accuracy minus Nrp accuracy; RIF = Nrp accuracy minus Rp- accuracy; timeouts and mean correct RT by condition.

## 5. Stimulus Layout Plan

- Screen name: study pair.
  - Stimulus IDs shown together: `study_category_text`, `study_exemplar_text`.
  - Layout anchors: category at `[0, 100]`; exemplar at `[0, -20]`.
  - Size/spacing: heights 34/48 px, wrap width 900 px.
  - Readability/overlap checks: 120 px center separation on a 1280×720 window; QA screenshots must show no overlap.
- Screen name: practice/final cued recall.
  - Stimulus IDs shown together: phase label, `cue_category_text`, `cue_stem_text`, `response_entry`, `submit_hint_text`.
  - Layout anchors: phase label `[0, 220]`, category `[0, 115]`, stem `[0, 25]`, response box `[0, -95]`, submit hint `[0, -210]`.
  - Size/spacing: response box 620×76 px; all text uses explicit height and wrap width.
  - Readability/overlap checks: at least 70 px between adjacent text baselines and 55 px from response-box edges.
- Screen name: distractor parity judgment.
  - Stimulus IDs shown together: `distractor_problem_text`, `distractor_left_label`, `distractor_right_label`.
  - Layout anchors: problem `[0, 80]`, labels `[-250, -130]` and `[250, -130]`.
  - Size/spacing: problem 54 px; option labels 30 px; 500 px horizontal separation.
  - Readability/overlap checks: explicit left/right grouping and QA screenshot review.

## 6. Trigger Plan

- Experiment: onset `1`, end `2`.
- Phase instruction screens: study `10`, practice `20`, distractor `30`, final test `40`.
- Trial onsets: study `11`, practice `21`, distractor `31`, final test Rp+ `41`, Rp- `42`, Nrp `43`.
- Responses: text submit `51`, distractor F `52`, distractor J `53`, timeout `59`.

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one explicit mode-aware flow that builds the session plan once and executes the four phase blocks sequentially through `BlockUnit.add_condition(...)`.
- `utils.py` used: yes.
- Exact purpose: deterministic cross-phase session planning, hashable plan payloads, response normalization, item-level scoring, and summary aggregation.
- Custom controller used: no. The paradigm has no adaptive online controller.
- Legacy/backward-compatibility fallback logic required: no.
- Text entry uses PsychoPy's config-defined editable `TextBox2` with `StimUnit.capture_response(...)` listening for Return; this preserves StimUnit timing, trigger, context, and data paths without a manual drawing loop.

## 8. Inference Log

- Decision: translate and curate eight taxonomic categories with six Chinese exemplars each, requiring unique first characters within each category.
  - Why inference was required: the classic papers used English category norms that are not participant-language appropriate.
  - Citation-supported rationale: the translation preserves the cited category-exemplar and unique-stem structure while using SimHei for Chinese glyph coverage.
- Decision: implement the 20-minute unrelated retention interval as 120 ten-second arithmetic parity trials.
  - Why inference was required: W2043527309 reports an unrelated causal-reasoning experiment but does not provide reusable materials.
  - Citation-supported rationale: the implementation preserves the 20-minute filled interval and prevents rehearsal without altering RIF factors.
- Decision: use itemwise category-plus-first-character final cues with a 7-second window.
  - Why inference was required: W2043527309 Experiment 1 used 30-second category free recall, which requires unconstrained list entry; W2054727733 provides a computer-compatible itemwise cued-recall control for output interference.
  - Citation-supported rationale: W2054727733 directly reports category-plus-letter final cues and a 7-second response interval.
- Decision: QA/simulation profiles shorten phase counts and timing while preserving Rp+, Rp-, Nrp assignment, all four stages, text-entry timeout paths, and distractor response paths.
  - Why inference was required: full human duration is inappropriate for automated gates.
  - Citation-supported rationale: preview-only shortening is permitted by the task-build validation contract and does not change single-trial semantics.
