#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml
from jsonschema import Draft202012Validator


LDM_ID_RE = re.compile(
    r"^ldm://(?P<name>[a-zA-Z0-9_\-]+)/(?P<version>[0-9]+\.[0-9]+\.[0-9]+)$"
)


@dataclass(frozen=True)
class G03Config:
    ldm_contract: str
    artifact: str
    mode: str  # strict | lenient


def read_story_front_matter(story_path: Path) -> Dict[str, Any]:
    text = story_path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        raise ValueError(f"No front matter found in story: {story_path}")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Malformed front matter in story: {story_path}")

    front_matter = yaml.safe_load(parts[1]) or {}
    if not isinstance(front_matter, dict):
        raise ValueError("Front matter must be a YAML mapping")

    return front_matter


def extract_g03_config(front_matter: Dict[str, Any]) -> G03Config:
    guardrails = front_matter.get("guardrails", {})
    g03 = guardrails.get("G03")

    if not isinstance(g03, dict):
        raise ValueError("guardrails.G03 must be declared as a mapping")

    ldm_contract = g03.get("ldm_contract")
    artifact = g03.get("artifact")
    mode = g03.get("mode", "strict")

    if not isinstance(ldm_contract, str) or not ldm_contract:
        raise ValueError("G03 requires a non-empty ldm_contract")
    if not isinstance(artifact, str) or not artifact:
        raise ValueError("G03 requires a non-empty artifact")
    if mode not in ("strict", "lenient"):
        raise ValueError("G03 mode must be 'strict' or 'lenient'")

    return G03Config(
        ldm_contract=ldm_contract,
        artifact=artifact,
        mode=mode,
    )


def resolve_contract_path(ldm_contract: str, repo_root: Path) -> Path:
    match = LDM_ID_RE.match(ldm_contract)
    if not match:
        raise ValueError(f"Invalid LDM contract id: {ldm_contract}")

    name = match.group("name")
    version = match.group("version")

    path = (
        repo_root
        / "docs"
        / "ldm"
        / "contracts"
        / name
        / version
        / "schema.json"
    )

    if not path.exists():
        raise FileNotFoundError(f"LDM schema not found: {path}")

    return path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_schema(schema: Dict[str, Any], mode: str) -> Dict[str, Any]:
    if mode == "strict":
        return schema

    def strip_additional_props(node: Any) -> Any:
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                if k == "additionalProperties" and v is False:
                    continue
                out[k] = strip_additional_props(v)
            return out
        if isinstance(node, list):
            return [strip_additional_props(x) for x in node]
        return node

    return strip_additional_props(schema)


def validate_instance(schema: Dict[str, Any], instance: Any) -> List[Dict[str, str]]:
    validator = Draft202012Validator(schema)
    errors: List[Dict[str, str]] = []

    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        path = "$"
        if err.path:
            for p in err.path:
                path += f".{p}" if isinstance(p, str) else f"[{p}]"

        errors.append(
            {
                "path": path,
                "rule": err.validator or "validation",
                "detail": err.message,
            }
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="G03 Guardrail — LDM Adherence")
    parser.add_argument("--story", required=True, help="Path to story markdown file")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--story-id", help="Override story_id")
    parser.add_argument("--out", help="Output path for guardrail result JSON")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    story_path = Path(args.story).resolve()

    front_matter = read_story_front_matter(story_path)
    g03 = extract_g03_config(front_matter)

    story_id = args.story_id or front_matter.get("story_id") or story_path.stem

    schema_path = resolve_contract_path(g03.ldm_contract, repo_root)
    schema = load_json(schema_path)

    if schema.get("$id") != g03.ldm_contract:
        raise ValueError(
            f"Schema $id mismatch: expected {g03.ldm_contract}, "
            f"found {schema.get('$id')}"
        )

    schema = normalize_schema(schema, g03.mode)

    artifact_path = (
        repo_root
        / "evidence"
        / "runtime_outputs"
        / story_id
        / f"{g03.artifact}.json"
    )

    if not artifact_path.exists():
        raise FileNotFoundError(f"Runtime artifact not found: {artifact_path}")

    instance = load_json(artifact_path)
    errors = validate_instance(schema, instance)
    passed = len(errors) == 0

    result = {
        "guardrail_id": "G03",
        "passed": passed,
        "message": "LDM validation passed"
        if passed
        else f"LDM validation failed for {g03.ldm_contract}",
        "contract_id": g03.ldm_contract,
        "artifact_path": str(artifact_path.relative_to(repo_root)).replace("\\", "/"),
        "errors": errors,
        "warnings_count": 0,
        "warnings": [],
    }

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    else:
        print(json.dumps(result, indent=2))

    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
