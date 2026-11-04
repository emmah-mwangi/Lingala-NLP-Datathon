"""
Prediction interface.

Wraps the model pack produced by train.py so that app.py and any future
interface (CLI, API) call a single, stable function rather than reaching
into the pack dict directly.

This module has no dependency on Streamlit and can be imported and tested
independently of the UI.
"""

from __future__ import annotations

from typing import Any

from core import FRIENDLY, extract  # Tatyana's shared module — do not duplicate


class PredictionResult:
    """Holds the output of a single prediction."""

    __slots__ = ("label", "friendly_label", "probability", "slots", "track")

    def __init__(
        self,
        label: str,
        probability: float,
        slots: list[dict[str, Any]],
        track: str,
    ) -> None:
        self.label = label
        self.friendly_label = FRIENDLY.get(label, label)
        self.probability = probability
        self.slots = slots
        self.track = track

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "friendly_label": self.friendly_label,
            "probability": self.probability,
            "slots": self.slots,
            "track": self.track,
        }


def predict(text: str, pack: dict[str, Any]) -> PredictionResult:
    """Run a single prediction against a loaded model pack.

    Args:
        text: The input utterance (any language the model was trained on).
        pack: The dict returned by data_loader.load_model_pack().

    Returns:
        A PredictionResult with label, friendly label, probability and slots.

    Raises:
        ValueError: if *text* is empty after stripping whitespace.
    """
    text = text.strip()
    if not text:
        raise ValueError("Input text must not be empty.")

    model = pack["model"]
    label: str = model.predict([text])[0]
    proba: float = float(max(model.predict_proba([text])[0]))

    slots: list[dict[str, Any]] = []
    if pack["track"] == "semantic":
        slots = extract(text, pack["slot_memory"])

    return PredictionResult(label=label, probability=proba, slots=slots, track=pack["track"])
