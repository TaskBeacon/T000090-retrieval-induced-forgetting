from __future__ import annotations

from contextlib import nullcontext
from functools import partial
from pathlib import Path
from typing import Any

import pandas as pd
from psychopy import core

from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    next_trial_id,
    parse_task_run_options,
    runtime_context,
    set_trial_context,
)

from src import generate_rif_session_plan, run_trial, summarize_final_test


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}
PHASE_SCREENS = {
    "study": ("study_instruction_text", "study_instruction_onset"),
    "retrieval_practice": ("practice_instruction_text", "practice_instruction_onset"),
    "distractor": ("distractor_instruction_text", "distractor_instruction_onset"),
    "final_test": ("final_test_instruction_text", "final_test_instruction_onset"),
}


def _show_screen(
    *,
    stim_bank: StimBank,
    win: Any,
    kb: Any,
    trigger_runtime: Any,
    settings: TaskSettings,
    stim_name: str,
    phase: str,
    trigger_name: str | None = None,
    format_values: dict[str, Any] | None = None,
) -> None:
    continue_key = str(getattr(settings, "continue_key", "space")).strip().lower() or "space"
    trial_id = int(next_trial_id())
    unit = StimUnit(phase, win, kb, runtime=trigger_runtime)
    stimulus = (
        stim_bank.get_and_format(stim_name, **format_values)
        if format_values
        else stim_bank.get(stim_name)
    )
    unit.add_stim(stimulus)
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=None,
        valid_keys=[continue_key],
        block_id=phase,
        condition_id=phase,
        task_factors={"stage": phase},
        stim_id=stim_name,
    )
    if trigger_name:
        trigger_runtime.send(settings.triggers.get(trigger_name))
    unit.wait_and_continue(keys=[continue_key])


def _execute_phase(
    *,
    phase: str,
    phase_idx: int,
    conditions: list[Any],
    settings: TaskSettings,
    win: Any,
    kb: Any,
    stim_bank: StimBank,
    trigger_runtime: Any,
) -> list[dict[str, Any]]:
    block = (
        BlockUnit(
            block_id=phase,
            block_idx=phase_idx,
            settings=settings,
            window=win,
            keyboard=kb,
        )
        .add_condition(conditions)
        .on_start(lambda _: trigger_runtime.send(settings.triggers.get("block_onset")))
        .on_end(lambda _: trigger_runtime.send(settings.triggers.get("block_end")))
        .run_trial(
            partial(
                run_trial,
                stim_bank=stim_bank,
                trigger_runtime=trigger_runtime,
                block_id=phase,
                block_idx=phase_idx,
            )
        )
    )
    return list(block.get_all_data())


def run(options: TaskRunOptions) -> None:
    """Run the canonical four-phase RIF task in human, QA, or simulation mode."""

    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path))

    output_dir: Path | None = None
    runtime_scope = nullcontext()
    runtime_ctx = None
    if options.mode in ("qa", "sim"):
        runtime_ctx = context_from_config(task_dir=task_root, config=cfg, mode=options.mode)
        output_dir = runtime_ctx.output_dir
        runtime_scope = runtime_context(runtime_ctx)

    with runtime_scope:
        if options.mode == "qa":
            subject_data = {"subject_id": "qa090"}
        elif options.mode == "sim":
            participant_id = "sim090"
            if runtime_ctx is not None and runtime_ctx.session is not None:
                participant_id = str(runtime_ctx.session.participant_id or participant_id)
            subject_data = {"subject_id": participant_id}
        else:
            subject_data = SubInfo(cfg["subform_config"]).collect()

        settings = TaskSettings.from_dict(cfg["task_config"])
        if options.mode in ("qa", "sim") and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.save_path = str(output_dir)
        settings.add_subinfo(subject_data)
        if options.mode in ("qa", "sim") and output_dir is not None:
            prefix = "qa" if options.mode == "qa" else "sim"
            settings.res_file = str(output_dir / f"{prefix}_trace.csv")
            settings.log_file = str(output_dir / f"{prefix}_psychopy.log")
            settings.json_file = str(output_dir / f"{prefix}_settings.json")

        settings.triggers = cfg["trigger_config"]
        trigger_runtime = (
            initialize_triggers(mock=True)
            if options.mode in ("qa", "sim")
            else initialize_triggers(cfg)
        )
        win, kb = initialize_exp(settings)
        stim_bank = StimBank(win, cfg["stim_config"]).preload_all()
        settings.save_to_json()

        trigger_runtime.send(settings.triggers.get("exp_onset"))
        _show_screen(
            stim_bank=stim_bank,
            win=win,
            kb=kb,
            trigger_runtime=trigger_runtime,
            settings=settings,
            stim_name="instruction_text",
            phase="general_instruction",
        )

        plan = generate_rif_session_plan(settings, subject_data["subject_id"])
        all_rows: list[dict[str, Any]] = []
        for phase_idx, phase in enumerate(("study", "retrieval_practice", "distractor", "final_test")):
            stim_name, trigger_name = PHASE_SCREENS[phase]
            _show_screen(
                stim_bank=stim_bank,
                win=win,
                kb=kb,
                trigger_runtime=trigger_runtime,
                settings=settings,
                stim_name=stim_name,
                phase=f"{phase}_instruction",
                trigger_name=trigger_name,
            )
            all_rows.extend(
                _execute_phase(
                    phase=phase,
                    phase_idx=phase_idx,
                    conditions=plan[phase],
                    settings=settings,
                    win=win,
                    kb=kb,
                    stim_bank=stim_bank,
                    trigger_runtime=trigger_runtime,
                )
            )

        summary = summarize_final_test(all_rows)
        pd.DataFrame(all_rows).to_csv(settings.res_file, index=False)

        _show_screen(
            stim_bank=stim_bank,
            win=win,
            kb=kb,
            trigger_runtime=trigger_runtime,
            settings=settings,
            stim_name="good_bye_text",
            phase="good_bye",
            trigger_name="good_bye_onset",
            format_values={
                "rp_plus_accuracy": f"{summary['rp_plus_accuracy']:.1%}",
                "rp_minus_accuracy": f"{summary['rp_minus_accuracy']:.1%}",
                "nrp_accuracy": f"{summary['nrp_accuracy']:.1%}",
                "facilitation_score": f"{summary['facilitation_score']:.3f}",
                "rif_score": f"{summary['rif_score']:.3f}",
                "timeouts": int(summary["final_test_timeouts"]),
            },
        )
        trigger_runtime.send(settings.triggers.get("exp_end"))
        trigger_runtime.close()
        win.close()
        core.quit()


def main() -> None:
    task_root = Path(__file__).resolve().parent
    options = parse_task_run_options(
        task_root=task_root,
        description="Run the Retrieval-Induced Forgetting task in human/qa/sim mode.",
        default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
        modes=MODES,
    )
    run(options)


if __name__ == "__main__":
    main()
