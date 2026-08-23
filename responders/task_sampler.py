from __future__ import annotations

import random as _py_random
from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    hit_rate: float = 0.8
    rt_mean_s: float = 0.25
    rt_sd_s: float = 0.04

    def __post_init__(self) -> None:
        self._rng: Any = None
        self.hit_rate = min(1.0, max(0.0, float(self.hit_rate)))

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _random(self) -> float:
        return float(self._rng.random()) if self._rng is not None else float(_py_random.random())

    def _normal(self) -> float:
        if self._rng is not None and hasattr(self._rng, "normal"):
            return float(self._rng.normal(self.rt_mean_s, self.rt_sd_s))
        if self._rng is not None and hasattr(self._rng, "gauss"):
            return float(self._rng.gauss(self.rt_mean_s, self.rt_sd_s))
        return float(_py_random.gauss(self.rt_mean_s, self.rt_sd_s))

    def act(self, obs: Observation) -> Action:
        valid_keys = list(obs.valid_keys or [])
        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "rif_sampler", "reason": "no_valid_keys"})

        rt = max(0.02, self._normal())
        if obs.phase == "distractor_problem":
            correct_key = str((obs.task_factors or {}).get("correct_key", valid_keys[0]))
            if self._random() <= self.hit_rate and correct_key in valid_keys:
                key = correct_key
            else:
                key = next((candidate for candidate in valid_keys if candidate != correct_key), valid_keys[0])
            return Action(key=key, rt_s=rt, meta={"source": "rif_sampler", "stage": "distractor"})

        if obs.phase == "practice_cue":
            return Action(key=valid_keys[0], rt_s=rt, meta={"source": "rif_sampler", "stage": "cue_response"})

        if obs.phase == "final_test_cue":
            return Action(key=valid_keys[0], rt_s=rt, meta={"source": "rif_sampler", "stage": "cue_response"})

        return Action(key=valid_keys[0], rt_s=rt, meta={"source": "rif_sampler"})
