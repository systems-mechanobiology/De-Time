from __future__ import annotations

from typing import Any, Dict, Tuple

from .registry import MethodRegistry
from .schemas import (
    MethodMetadataModel,
    RecommendationItemModel,
    RecommendationRequestModel,
    RecommendationResponseModel,
)


def _score_method(metadata: MethodMetadataModel, request: RecommendationRequestModel) -> Tuple[float, list[str], str | None]:
    channels = request.channels
    reasons: list[str] = []
    score = 0.0

    if channels > 1 and metadata.input_mode == "univariate":
        return score, reasons, "univariate_only"
    if channels == 1 and metadata.input_mode == "multivariate":
        return score, reasons, "requires_multivariate_input"
    if request.require_native and not metadata.native_backed:
        return score, reasons, "native_required"
    if metadata.dependency_tier == "optional-backend" and not request.allow_optional_backends:
        return score, reasons, "optional_backend_disabled"
    if request.length < metadata.min_length:
        return score, reasons, f"series_too_short(min={metadata.min_length})"

    maturity_bonus = {
        "flagship": 4.0,
        "stable": 2.5,
        "optional-backend": 1.5,
        "experimental": 0.5,
    }[metadata.maturity]
    score += maturity_bonus
    reasons.append(f"maturity:{metadata.maturity}")

    if metadata.native_backed:
        score += 1.5
        reasons.append("native_backed")

    if channels > 1:
        if metadata.multivariate_support == "shared-model":
            score += 4.5
            reasons.append("shared_multivariate")
        elif metadata.multivariate_support == "channelwise":
            score += 2.0
            reasons.append("channelwise_multivariate")
    else:
        if metadata.input_mode == "univariate":
            score += 1.0
            reasons.append("univariate_ready")

    if request.prefer == "speed":
        if metadata.native_backed:
            score += 3.0
            reasons.append("speed_native_bonus")
        if metadata.name in {"STD", "STDR", "MA_BASELINE"}:
            score += 1.5
            reasons.append("speed_shortlist")
    elif request.prefer == "accuracy":
        if metadata.name in {"SSA", "MSSA", "STDR"}:
            score += 2.5
            reasons.append("accuracy_shortlist")
        if channels > 1 and metadata.multivariate_support == "shared-model":
            score += 1.5
            reasons.append("multivariate_accuracy_bonus")
        if metadata.maturity == "flagship":
            score += 1.0
    else:
        if metadata.name in {"SSA", "STD", "STDR", "MSSA"}:
            score += 1.5
            reasons.append("balanced_flagship")

    if request.length >= 128 and metadata.native_backed:
        score += 0.75
        reasons.append("long_series_native")
    if request.length < 48 and metadata.name in {"STD", "STDR", "MA_BASELINE", "STL"}:
        score += 0.75
        reasons.append("short_series_friendly")

    return score, reasons, None


def recommend_methods(request: RecommendationRequestModel | Dict[str, Any]) -> RecommendationResponseModel:
    req = (
        request
        if isinstance(request, RecommendationRequestModel)
        else RecommendationRequestModel.model_validate(request)
    )
    recommendations: list[RecommendationItemModel] = []
    rejected: Dict[str, str] = {}

    for entry in MethodRegistry.list_catalog():
        metadata = MethodMetadataModel.model_validate(entry)
        score, reason_codes, rejection = _score_method(metadata, req)
        if rejection is not None:
            rejected[metadata.name] = rejection
            continue
        recommendations.append(
            RecommendationItemModel(
                method=metadata.name,
                score=round(score, 3),
                rank=0,
                reason_codes=reason_codes,
                summary=metadata.summary,
                metadata=metadata,
            )
        )

    recommendations.sort(key=lambda item: (-item.score, item.method))
    sliced = recommendations[: req.top_k]
    for index, item in enumerate(sliced, start=1):
        item.rank = index

    return RecommendationResponseModel(
        request=req,
        recommendations=sliced,
        rejected_methods=rejected,
    )
