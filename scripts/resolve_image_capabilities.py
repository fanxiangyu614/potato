#!/usr/bin/env python3
"""Resolve image tool candidates into unavailable, single, multiple, or failed states."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def candidate_label(candidate: dict[str, Any]) -> str:
    return "／".join(
        value for value in (candidate["tool"], candidate.get("model")) if value
    )


def decide(
    candidates: list[dict[str, Any]],
    task: str,
    *,
    choice: str | None = None,
    default_choice: str | None = None,
    failed: str | None = None,
) -> dict[str, Any]:
    if task not in {"generate", "edit"}:
        raise ValueError("task 必须是 generate 或 edit")

    available: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("每个候选必须是对象")
        tool = candidate.get("tool")
        model = candidate.get("model")
        capabilities = candidate.get("capabilities")
        status = candidate.get("status")
        if not isinstance(tool, str) or not tool.strip():
            raise ValueError("候选 tool 必须是非空文本")
        if model is not None and (not isinstance(model, str) or not model.strip()):
            raise ValueError("候选 model 必须是非空文本或 null")
        if not isinstance(capabilities, list) or any(
            capability not in {"generate", "edit"} for capability in capabilities
        ):
            raise ValueError("候选 capabilities 只能包含 generate、edit")
        if status not in {"callable", "requires_auth", "unknown"}:
            raise ValueError("候选 status 无效")
        normalized = {
            "tool": tool.strip(),
            "model": model.strip() if isinstance(model, str) else None,
            "capabilities": list(dict.fromkeys(capabilities)),
            "status": status,
        }
        key = (normalized["tool"], normalized["model"] or "")
        if status == "callable" and task in capabilities and key not in seen:
            seen.add(key)
            available.append(normalized)

    if failed is not None:
        failed_candidate = _select(available, failed)
        return {
            "state": "failed",
            "message": f"生图能力：调用「{candidate_label(failed_candidate)}」失败，已暂停；不会自动改用其他方案。",
            "selected": failed_candidate,
            "candidates": available,
            "automatic_fallback": False,
        }
    # An explicit/current-task choice must not silently become another tool,
    # even when only that other tool remains available.
    requested = choice if choice is not None else default_choice
    if requested is not None:
        selected = _select(available, requested)
        return {
            "state": "selected",
            "message": f"生图能力：使用已选方案「{candidate_label(selected)}」。",
            "selected": selected,
            "candidates": available,
            "automatic_fallback": False,
        }
    if not available:
        return {
            "state": "unavailable",
            "message": "生图能力：当前会话没有可调用的生图工具，无法直接出图。我可以先交付完整提示词和图片规格。",
            "selected": None,
            "candidates": [],
            "automatic_fallback": False,
        }
    if len(available) == 1:
        selected = available[0]
        return {
            "state": "single",
            "message": f"生图能力：已检测到一个可用方案，将使用「{candidate_label(selected)}」。",
            "selected": selected,
            "candidates": available,
            "automatic_fallback": False,
        }
    return {
        "state": "multiple",
        "message": "生图能力：存在多个方案且未提供适用的已选或默认方案，请确认实际差异后选择。",
        "selected": None,
        "candidates": available,
        "automatic_fallback": False,
    }


def _select(candidates: list[dict[str, Any]], choice: str) -> dict[str, Any]:
    value = str(choice).strip()
    if value.isdigit():
        index = int(value) - 1
        if 0 <= index < len(candidates):
            return candidates[index]
    matches = [
        candidate
        for candidate in candidates
        if value in {
            candidate["tool"],
            candidate.get("model") or "",
            candidate_label(candidate),
        }
    ]
    if len(matches) != 1:
        raise ValueError(f"无法唯一匹配图片方案：{choice}")
    return matches[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, choices=("generate", "edit"))
    parser.add_argument("--candidates-json", required=True)
    parser.add_argument("--choice")
    parser.add_argument("--default-choice", help="已经确认适用且在授权范围内的默认方案")
    parser.add_argument("--failed")
    args = parser.parse_args(argv)
    candidates = json.loads(args.candidates_json)
    if not isinstance(candidates, list):
        raise ValueError("candidates-json 必须是数组")
    print(json.dumps(
        decide(candidates, args.task, choice=args.choice, default_choice=args.default_choice, failed=args.failed),
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(2)
