from __future__ import annotations

from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from src.utils import normalize_response


def _record_value(record: dict[str, Any], prefix: str, name: str, default: Any = None) -> Any:
    if name in record:
        return record.get(name, default)
    return record.get(f"{prefix}_{name}", default)


def _trigger(settings: Any, name: str) -> Any:
    return (getattr(settings, "triggers", {}) or {}).get(name)


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Run one preplanned presentation from the four-phase RIF session."""

    plan = condition.to_dict()
    stage = str(plan["stage"])
    trial_id = int(next_trial_id())
    block_id_value = str(block_id or stage)
    condition_id = str(plan["condition_id"])
    task_factors = dict(plan)
    task_factors.pop("condition_id", None)

    row: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_id_value,
        "block_idx": int(block_idx or 0),
        "stage": stage,
        "condition_id": condition_id,
        "item_status": plan.get("item_status"),
        "category": plan.get("category"),
        "exemplar": plan.get("exemplar"),
        "cue": plan.get("cue"),
        "practice_repetition": plan.get("practice_repetition"),
        "problem": plan.get("problem"),
        "parity": plan.get("parity"),
        "correct_key": plan.get("correct_key"),
        "response_key": "",
        "response_text": "",
        "response_rt": None,
        "response_correct": False,
        "timed_out": False,
    }

    if stage == "study":
        unit = StimUnit("study_item", win, kb, runtime=trigger_runtime)
        unit.add_stim(stim_bank.get_and_format("study_category_text", category=plan["category"]))
        unit.add_stim(stim_bank.get_and_format("study_exemplar_text", exemplar=plan["exemplar"]))
        duration = float(getattr(settings, "study_duration_s", 5.0))
        set_trial_context(
            unit,
            trial_id=trial_id,
            phase="study_item",
            deadline_s=duration,
            valid_keys=[],
            block_id=block_id_value,
            condition_id=condition_id,
            task_factors=task_factors,
            stim_id="study_category_text+study_exemplar_text",
        )
        unit.show(duration=duration, onset_trigger=_trigger(settings, "study_onset")).to_dict(row)
        return row

    if stage in ("retrieval_practice", "final_test"):
        phase_name = "practice" if stage == "retrieval_practice" else "final_test"
        phase_stimulus = "practice_phase_label" if stage == "retrieval_practice" else "final_test_phase_label"
        response_box = stim_bank.rebuild("response_entry", update_cache=False, text="", editable=True)
        response_box.hasFocus = True

        unit = StimUnit(f"{phase_name}_cue", win, kb, runtime=trigger_runtime)
        unit.add_stim(stim_bank.get(phase_stimulus))
        unit.add_stim(stim_bank.get_and_format("cue_category_text", category=plan["category"]))
        unit.add_stim(stim_bank.get_and_format("cue_stem_text", cue=plan["cue"]))
        unit.add_stim(response_box)
        unit.add_stim(stim_bank.get("submit_hint_text"))

        duration = float(
            getattr(
                settings,
                "practice_response_window_s" if stage == "retrieval_practice" else "final_test_response_window_s",
                10.0 if stage == "retrieval_practice" else 7.0,
            )
        )
        submit_key = str(getattr(settings, "submit_key", "return")).strip().lower() or "return"
        onset_name = "practice_onset" if stage == "retrieval_practice" else f"final_{plan['item_status']}_onset"
        set_trial_context(
            unit,
            trial_id=trial_id,
            phase=f"{phase_name}_cue",
            deadline_s=duration,
            valid_keys=[submit_key],
            block_id=block_id_value,
            condition_id=condition_id,
            task_factors=task_factors,
            stim_id=f"{phase_stimulus}+cue_category_text+cue_stem_text+response_entry",
        )
        unit.capture_response(
            keys=[submit_key],
            duration=duration,
            onset_trigger=_trigger(settings, onset_name),
            response_trigger={submit_key: _trigger(settings, "text_submit")},
            timeout_trigger=_trigger(settings, "response_timeout"),
        ).to_dict(row)
        response_box.editable = False

        response_text = str(response_box.getText() or "")
        response_key = str(_record_value(row, f"{phase_name}_cue", "response", "") or "")
        response_rt = _record_value(row, f"{phase_name}_cue", "rt", None)
        timed_out = not bool(response_key)
        row.update(
            {
                "response_key": response_key,
                "response_text": response_text,
                "response_rt": response_rt,
                "response_correct": normalize_response(response_text) == normalize_response(plan["exemplar"]),
                "timed_out": timed_out,
            }
        )
        return row

    if stage == "distractor":
        keys = dict(getattr(settings, "distractor_keys", {"odd": "f", "even": "j"}))
        valid_keys = [str(keys["odd"]), str(keys["even"])]
        correct_key = str(plan["correct_key"])
        unit = StimUnit("distractor_problem", win, kb, runtime=trigger_runtime)
        unit.add_stim(stim_bank.get_and_format("distractor_problem_text", problem=plan["problem"]))
        unit.add_stim(stim_bank.get("distractor_left_label"))
        unit.add_stim(stim_bank.get("distractor_right_label"))
        duration = float(getattr(settings, "distractor_trial_duration_s", 10.0))
        set_trial_context(
            unit,
            trial_id=trial_id,
            phase="distractor_problem",
            deadline_s=duration,
            valid_keys=valid_keys,
            block_id=block_id_value,
            condition_id=condition_id,
            task_factors=task_factors,
            stim_id="distractor_problem_text+distractor_left_label+distractor_right_label",
        )
        unit.capture_response(
            keys=valid_keys,
            correct_keys=[correct_key],
            duration=duration,
            onset_trigger=_trigger(settings, "distractor_onset"),
            response_trigger={
                valid_keys[0]: _trigger(settings, "distractor_f"),
                valid_keys[1]: _trigger(settings, "distractor_j"),
            },
            timeout_trigger=_trigger(settings, "response_timeout"),
            terminate_on_response=False,
        ).to_dict(row)
        response_key = str(_record_value(row, "distractor_problem", "response", "") or "")
        row.update(
            {
                "response_key": response_key,
                "response_rt": _record_value(row, "distractor_problem", "rt", None),
                "response_correct": response_key == correct_key,
                "timed_out": not bool(response_key),
            }
        )
        return row

    raise ValueError(f"Unsupported RIF stage: {stage}")
