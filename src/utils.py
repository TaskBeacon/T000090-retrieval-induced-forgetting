from __future__ import annotations

import hashlib
import random
import unicodedata
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any


FINAL_ITEM_STATUSES = ("rp_plus", "rp_minus", "nrp")


class TrialPlan(str):
    """Hashable condition label carrying one immutable planned presentation."""

    def __new__(cls, *, label: str, **payload: Any):
        instance = super().__new__(cls, label)
        instance.label = label
        instance._payload = MappingProxyType({"label": label, **payload})
        return instance

    def to_dict(self) -> dict[str, Any]:
        return dict(self._payload)


def normalize_response(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    return "".join(text.split()).casefold()


def _participant_seed(overall_seed: int, participant_id: Any) -> int:
    digest = hashlib.sha256(str(participant_id).encode("utf-8")).digest()
    return int(overall_seed) + int.from_bytes(digest[:4], "big")


def _make_cue(exemplar: str) -> str:
    visible = str(exemplar).strip()
    if not visible:
        raise ValueError("Exemplars must not be blank.")
    return visible[0] + "＿" * max(2, len(visible) - 1)


def _validate_item_bank(
    category_bank: Mapping[str, Any],
    *,
    category_count: int,
    items_per_category: int,
) -> list[tuple[str, list[str]]]:
    categories = list(category_bank.items())[:category_count]
    if len(categories) != category_count:
        raise ValueError(f"Expected {category_count} categories, found {len(categories)}.")

    validated: list[tuple[str, list[str]]] = []
    for category, raw_items in categories:
        items = [str(item).strip() for item in list(raw_items)[:items_per_category]]
        if len(items) != items_per_category or any(not item for item in items):
            raise ValueError(f"Category {category!r} must contain {items_per_category} nonblank exemplars.")
        first_chars = [item[0] for item in items]
        if len(set(first_chars)) != len(first_chars):
            raise ValueError(f"Category {category!r} has non-unique first-character cues.")
        validated.append((str(category), items))
    return validated


def generate_rif_session_plan(settings: Any, participant_id: Any) -> dict[str, list[TrialPlan]]:
    """Create one deterministic cross-phase RIF session plan."""

    category_count = int(getattr(settings, "category_count", 8))
    items_per_category = int(getattr(settings, "items_per_category", 6))
    practiced_category_count = int(getattr(settings, "practiced_category_count", category_count // 2))
    practiced_items_per_category = int(getattr(settings, "practiced_items_per_category", items_per_category // 2))
    practice_repetitions = int(getattr(settings, "practice_repetitions", 3))
    distractor_trials = int(getattr(settings, "distractor_trials", 120))

    if not 0 < practiced_category_count < category_count:
        raise ValueError("practiced_category_count must be between 1 and category_count - 1.")
    if not 0 < practiced_items_per_category < items_per_category:
        raise ValueError("practiced_items_per_category must be between 1 and items_per_category - 1.")
    if practice_repetitions < 1 or distractor_trials < 1:
        raise ValueError("practice_repetitions and distractor_trials must be positive.")

    category_bank = getattr(settings, "category_bank", {})
    if not isinstance(category_bank, Mapping):
        raise TypeError("task.category_bank must be a mapping.")
    categories = _validate_item_bank(
        category_bank,
        category_count=category_count,
        items_per_category=items_per_category,
    )

    session_seed = _participant_seed(int(getattr(settings, "overall_seed", 90090)), participant_id)
    rng = random.Random(session_seed)
    category_order = list(range(category_count))
    rng.shuffle(category_order)
    practiced_category_indexes = set(category_order[:practiced_category_count])

    items: list[dict[str, Any]] = []
    for category_index, (category, exemplars) in enumerate(categories):
        item_order = list(range(items_per_category))
        rng.shuffle(item_order)
        rp_plus_indexes = (
            set(item_order[:practiced_items_per_category])
            if category_index in practiced_category_indexes
            else set()
        )
        for item_index, exemplar in enumerate(exemplars):
            if category_index not in practiced_category_indexes:
                item_status = "nrp"
            elif item_index in rp_plus_indexes:
                item_status = "rp_plus"
            else:
                item_status = "rp_minus"
            items.append(
                {
                    "category": category,
                    "exemplar": exemplar,
                    "cue": _make_cue(exemplar),
                    "category_index": category_index,
                    "item_index": item_index,
                    "item_status": item_status,
                    "category_practiced": category_index in practiced_category_indexes,
                }
            )

    study_items = list(items)
    rng.shuffle(study_items)
    study = [
        TrialPlan(
            label="study",
            stage="study",
            condition_id=f"study_{index + 1:03d}",
            study_order=index + 1,
            **item,
        )
        for index, item in enumerate(study_items)
    ]

    rp_plus_items = [item for item in items if item["item_status"] == "rp_plus"]
    practice: list[TrialPlan] = []
    for repetition in range(1, practice_repetitions + 1):
        repetition_items = list(rp_plus_items)
        rng.shuffle(repetition_items)
        for item in repetition_items:
            practice.append(
                TrialPlan(
                    label="rp_plus",
                    stage="retrieval_practice",
                    condition_id=f"practice_r{repetition}_{len(practice) + 1:03d}",
                    practice_repetition=repetition,
                    **item,
                )
            )

    distractor_keys = dict(getattr(settings, "distractor_keys", {"odd": "f", "even": "j"}))
    distractor: list[TrialPlan] = []
    for index in range(distractor_trials):
        left = rng.randint(11, 69)
        right = rng.randint(2, 29)
        answer = left + right
        parity = "even" if answer % 2 == 0 else "odd"
        distractor.append(
            TrialPlan(
                label="distractor",
                stage="distractor",
                condition_id=f"distractor_{index + 1:03d}",
                problem=f"{left} + {right} = {answer}",
                answer=answer,
                parity=parity,
                correct_key=str(distractor_keys[parity]),
            )
        )

    critical = [item for item in items if item["item_status"] in ("rp_minus", "nrp")]
    strengthened = [item for item in items if item["item_status"] == "rp_plus"]
    rng.shuffle(critical)
    rng.shuffle(strengthened)
    final_order = critical + strengthened
    final_test = [
        TrialPlan(
            label=str(item["item_status"]),
            stage="final_test",
            condition_id=f"final_{index + 1:03d}_{item['item_status']}",
            final_order=index + 1,
            output_tier="critical_first" if item["item_status"] != "rp_plus" else "rp_plus_last",
            **item,
        )
        for index, item in enumerate(final_order)
    ]

    return {
        "study": study,
        "retrieval_practice": practice,
        "distractor": distractor,
        "final_test": final_test,
    }


def summarize_final_test(rows: list[dict[str, Any]]) -> dict[str, Any]:
    final_rows = [row for row in rows if row.get("stage") == "final_test"]
    rates: dict[str, float] = {}
    mean_rts: dict[str, float | None] = {}
    for status in FINAL_ITEM_STATUSES:
        status_rows = [row for row in final_rows if row.get("item_status") == status]
        rates[status] = (
            sum(bool(row.get("response_correct", False)) for row in status_rows) / len(status_rows)
            if status_rows
            else 0.0
        )
        correct_rts = [
            float(row["response_rt"])
            for row in status_rows
            if bool(row.get("response_correct", False)) and isinstance(row.get("response_rt"), (int, float))
        ]
        mean_rts[status] = sum(correct_rts) / len(correct_rts) if correct_rts else None

    return {
        "rp_plus_accuracy": rates["rp_plus"],
        "rp_minus_accuracy": rates["rp_minus"],
        "nrp_accuracy": rates["nrp"],
        "facilitation_score": rates["rp_plus"] - rates["nrp"],
        "rif_score": rates["nrp"] - rates["rp_minus"],
        "rp_plus_mean_correct_rt": mean_rts["rp_plus"],
        "rp_minus_mean_correct_rt": mean_rts["rp_minus"],
        "nrp_mean_correct_rt": mean_rts["nrp"],
        "final_test_timeouts": sum(bool(row.get("timed_out", False)) for row in final_rows),
        "final_test_trials": len(final_rows),
    }
