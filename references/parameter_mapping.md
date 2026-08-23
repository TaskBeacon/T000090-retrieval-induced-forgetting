# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `category_count` | `task.category_count` | `8` | `W2043527309` | Experiment 1 Method: eight six-item categories. | `direct` | Human profile only; QA/sim use four categories while preserving all item statuses. |
| `items_per_category` | `task.items_per_category` | `6` | `W2043527309` | Experiment 1 initial study used six items from each category. | `direct` | Each Chinese category contains six exemplars with unique first characters. |
| `practiced_category_count` | `task.practiced_category_count` | `4` | `W2043527309` | Four of eight categories received retrieval practice. | `direct` | Participant-seeded counterbalancing selects the four categories. |
| `practiced_items_per_category` | `task.practiced_items_per_category` | `3` | `W2043527309` | Three exemplars from each practiced category were retrieved. | `direct` | Remaining items in practiced categories are Rp-. |
| `practice_repetitions` | `task.practice_repetitions` | `3` | `W2043527309` | Each practiced exemplar was tested three times. | `direct` | Repetition orders are independently shuffled. |
| `study_duration_s` | `timing.study_duration_s` | `5.0` | `W2043527309` | Experiment 1 Procedure: five seconds to study each category-exemplar pair. | `direct` | Fixed duration. |
| `practice_response_window_s` | `timing.practice_response_window_s` | `10.0` | `W2043527309` | Experiment 1 Procedure: ten seconds to recall each practice cue. | `direct` | Return submits typed text earlier. |
| `retention_interval_s` | `task.distractor_trials` + `timing.distractor_trial_duration_s` | `120 × 10 s = 1200 s` | `W2043527309` | Experiment 1 used a 20-minute filled retention interval. | `adapted` | Arithmetic parity replaces the unspecified causal-reasoning materials. |
| `final_test_response_window_s` | `timing.final_test_response_window_s` | `7.0` | `W2054727733` | Final category-plus-letter stem tests allowed seven seconds. | `direct` | Itemwise typed cued recall controls output interference. |
| `final_test_order` | `src.utils.generate_rif_session_plan` | `Rp-/Nrp before Rp+` | `W2043527309`, `W2054727733` | Both papers explicitly address output interference and final-test ordering. | `adapted` | Critical competitors are tested before strengthened items. |
| `language` | `task.language` | `Chinese` | `W2043527309`, `W2054727733` | Papers require taxonomic category-exemplar pairs and unique stems, but used English materials. | `adapted` | Chinese translations preserve the relational structure and unique first-character cue constraint. |
| `distractor_keys` | `task.distractor_keys` | `{odd: f, even: j}` | `W2043527309` | The retention interval must contain an unrelated task; exact response mapping was not specified. | `inferred` | Symmetric keyboard mapping supports fixed-duration parity judgments. |
| `trigger_map` | `triggers.map` | `1-60` | `W2043527309`, `W2054727733` | Behavioral source papers do not define hardware event codes. | `inferred` | Unique codes are assigned by phase, item status, response, and timeout. |
