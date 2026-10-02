#!/usr/bin/env python3
"""Verify the migrated early-Issue subgraph against the immutable source snapshot."""
import hashlib
import json
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ara
from notes import parse_document, detail_fields


def audit(root=ROOT):
    data = ara.validate(root)
    mapping = json.loads((root / "migration/mapping.json").read_text())
    issue_map = {int(old): new for old, new in mapping["issues"].items()}
    source = yaml.safe_load((root / "migration/source/ara/trace/exploration_tree.yaml").read_text())["graph"]
    selected = {n["id"]: n for n in source if int(n["id"][1:4]) in issue_map}
    def node_id(old):
        found = ara.NODE.fullmatch(old)
        return f"I{issue_map[int(found[1])]:03}-N{int(found[2]):02}"
    source_edges = {(n["id"], t) for n in source for t in n["next"]}
    source_edges |= {(p, n["id"]) for n in source for p in n.get("also_depends_on", [])}
    external = {(a, b) for a, b in source_edges if b in selected and a not in selected}
    assert not external, external
    expected = {(node_id(a), node_id(b)) for a, b in source_edges if a in selected and b in selected}
    imported = {node_id(old) for old in selected}
    assert {n for n, v in data["ideas"].items() if v.get("issue") in issue_map.values()} == imported
    actual = {(p, key) for key in imported for p in data["ideas"][key]["depends_on"] if p != ara.ROOT_ID}
    assert expected == actual, (expected - actual, actual - expected)
    norm = lambda value: " ".join(str(value).split())
    payload_fields = set()
    for old_id, original in selected.items():
        new_id = node_id(old_id)
        converted = data["ideas"][new_id]
        for field in ("title", "type", "status", "provenance", "timestamp"):
            assert converted[field] == original[field], (new_id, field)
        old_proof = {re.sub(r"E([0-9]+)-", lambda m: f"E{issue_map[int(m[1])]:03}-", e) for e in original["evidence"]}
        assert set(converted["evidence"]) == old_proof, (new_id, "evidence")
        details = data["details"][new_id]
        for field, value in original.items():
            if field in {"id", "title", "type", "status", "provenance", "timestamp", "source_issues", "next", "also_depends_on", "evidence"}:
                continue
            if not value:
                continue
            assert field in details, (new_id, "missing original field", field)
            for text in value if isinstance(value, list) else [value]:
                assert norm(text) in norm(details[field]), (new_id, "changed original text", field)
            payload_fields.add((new_id, field))
        shared, sections = parse_document((root / data["issues"][converted["issue"]]["record"]).read_text())
        extracted = data["notes"][new_id]
        assert extracted == shared + sections[new_id][1]
        assert len(re.findall(r"(?m)^## I[0-9]+-N[0-9]+ ", extracted)) == 1
    manifest = json.loads((root / "migration/source-manifest.json").read_text())
    for path, digest in manifest.items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest, path
    report = {"source_commit": mapping["source_commit"], "source_issues": sorted(issue_map),
              "destination_issues": sorted(issue_map.values()), "imported_ideas": len(imported),
              "preserved_edges": len(expected), "preserved_payload_fields": len(payload_fields),
              "frozen_source_files_verified": len(manifest), "exact_memo_extractions": len(imported),
              "schema": "passed", "historical_simulations_rerun": False,
              "scope": "Structure, preserved original payload and local archive hashes; not empirical reproduction."}
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, ensure_ascii=False))
