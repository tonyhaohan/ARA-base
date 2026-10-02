import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ara
from notes import parse_document, extract_idea


class RecordsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write("ara/project.yaml", {"schema_version": 1, "repository": "example/research", "title": "Test", "root": ara.ROOT_ID})
        self.ideas = [{"id": ara.ROOT_ID, "type": "root", "title": "Start", "depends_on": []}]
        for n in (1, 2):
            self.ideas.append({"id": f"I{n:03}-N01", "issue": n, "type": "question", "title": f"Question {n}", "status": "open", "provenance": "user", "timestamp": "2026-10-02", "depends_on": [ara.ROOT_ID if n == 1 else "I001-N01"], "primary_dependency": ara.ROOT_ID if n == 1 else "I001-N01", "record": f"ara/issues/issue{n:03}.md", "evidence": [], "evidence_note": "Not yet tested"})
            issue = {"issue": n, "title": "Research", "url": f"https://github.com/example/research/issues/{n}", "branch": f"codex/issue{n}-research", "status": "completed", "outcome": "failed", "depends_on": [], "summary": "Failed attempt remains useful", "record": f"ara/issues/issue{n:03}.md", "execplan": f"docs/plans/issue{n:03}/ExecPlan.md", "best_ideas": [{"id": f"I{n:03}-N01", "reason": "Only recorded attempt, not a successful result"}], "promising_ideas": [{"id": f"I{n:03}-N01", "reason": "Specific next test remains"}]}
            self.write(f"ara/issues/issue{n:03}.yaml", issue)
            self.text(issue["record"], f"# Issue #{n} — Test\n\n## 统一信息\nFixed environment\n\n## I{n:03}-N01 Question\n\n### question\nBody {n}\n")
            self.text(issue["execplan"], "".join(f"## {h}\n\nOriginal {h}\n\n" for h in ("Goal", "User Raw Prompts", "Progress", "Next Steps", "Decisions", "Evidence and Recovery")))
        self.write("ara/trace/ideas.yaml", {"ideas": self.ideas})
        self.text("proof.txt", "Measured result: 1 ms\n")
        self.evidence = {"id": "E001-01", "kind": "test", "summary": "Result", "location": "proof.txt", "identity": {"sha256": hashlib.sha256((self.root / "proof.txt").read_bytes()).hexdigest()}, "reproduction": {"command": "example command"}, "result": "1 ms", "raw_availability": "bundled"}
        self.write("ara/evidence/index.yaml", {"evidence": [self.evidence]})
        self.write("ara/logic/claims.yaml", {"claims": []})
        self.write("ara/staging/observations.yaml", {"observations": []})

    def text(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def write(self, path, data):
        self.text(path, yaml.safe_dump(data, allow_unicode=True, sort_keys=False))

    def validate(self):
        return ara.validate(self.root)

    def test_independent_graphs_and_failed_highlights(self):
        data = self.validate()
        self.assertEqual(data["successors"]["I001-N01"], ["I002-N01"])
        self.assertEqual(data["issues"][2]["depends_on"], [])
        self.assertEqual(ara.counts(data)["ideas"], 2)

    def test_root_primary_and_cycle_rejections(self):
        changes = [lambda n: n.update(depends_on=[]), lambda n: n.update(primary_dependency="I002-N01"), lambda n: n.update(depends_on=[ara.ROOT_ID, "I002-N01"]), lambda n: n.update(depends_on=["I002-N01"], primary_dependency="I002-N01"), lambda n: n.update(next=[]), lambda n: n.update(issue=99)]
        for change in changes:
            with self.subTest(change=change):
                values = copy.deepcopy(self.ideas)
                change(values[1])
                self.write("ara/trace/ideas.yaml", {"ideas": values})
                with self.assertRaises(ValueError): self.validate()

    def test_highlights_must_exist_and_belong_to_issue(self):
        path = "ara/issues/issue001.yaml"
        original = yaml.safe_load((self.root / path).read_text())
        for values in ([], [{"id": "I002-N01", "reason": "wrong owner"}], [{"id": "I001-N01", "reason": ""}]):
            item = copy.deepcopy(original)
            item["best_ideas"] = values
            self.write(path, item)
            with self.assertRaises(ValueError): self.validate()

    def test_issue_cycles(self):
        for n, dep in ((1, 2), (2, 1)):
            path = f"ara/issues/issue{n:03}.yaml"
            item = yaml.safe_load((self.root / path).read_text())
            item["depends_on"] = [dep]
            self.write(path, item)
        with self.assertRaisesRegex(ValueError, "cycle"): self.validate()

    def test_evidence_integrity_and_path_confinement(self):
        self.text("proof.txt", "changed")
        with self.assertRaisesRegex(ValueError, "hash mismatch"): self.validate()
        self.evidence["location"] = "../outside"
        self.write("ara/evidence/index.yaml", {"evidence": [self.evidence]})
        with self.assertRaisesRegex(ValueError, "escapes"): self.validate()

    def test_claim_observation_event_references(self):
        observation = {"id": "O001-01", "issue": 1, "timestamp": "2026-10-02", "text": "Observation", "context": "Paired trial", "provenance": "ai-executed", "bound_to": ["I001-N01"], "promotion_condition": "Comparison complete"}
        self.write("ara/staging/observations.yaml", {"observations": [observation]})
        claim = {"id": "C001-01", "statement": "Claim", "conditions": "This fixture", "falsification": "Opposite result", "status": "supported", "provenance": "ai-suggested", "evidence": ["E001-01"], "observations": ["O001-01"]}
        self.write("ara/logic/claims.yaml", {"claims": [claim]})
        event = {"id": "EV001-01", "action": "crystallize", "timestamp": "2026-10-02", "provenance": "ai-executed", "from": ["O001-01"], "to": ["C001-01"], "trigger": "empirical_resolution", "evidence": ["E001-01"], "rationale": "Paired evidence"}
        session = {"id": "S001", "timestamp": "2026-10-02", "issues": [1], "summary": "Test", "events": [event]}
        self.write("ara/trace/sessions/s001.yaml", session)
        self.assertEqual(len(self.validate()["events"]), 1)
        event["from"] = ["I001-N01"]
        self.write("ara/trace/sessions/s001.yaml", session)
        with self.assertRaises(ValueError): self.validate()

    def test_memo_extraction_fences_and_no_neighbor_leak(self):
        text = "# Issue #1 — Demo\n## 统一信息\nCOMMON\n\n## I001-N01 First\nFIRST\n````md\n```\n## I001-N99 Fake\n````\n\n## I001-N02 Second\nSECOND\n"
        shared, nodes = parse_document(text)
        selected = extract_idea(text, "I001-N02")
        self.assertEqual(selected, shared + nodes["I001-N02"][1])
        self.assertNotIn("FIRST", selected)
        self.assertNotIn("Fake", selected)
        for bad in (text.replace("I001-N02", "I001-N01"), text + "\n~~~\n", text.replace("## I001-N02", "  ## I001-N02")):
            with self.assertRaises(ValueError): parse_document(bad)

    def test_duplicate_yaml_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate YAML"):
            ara.parse_yaml("id: first\nid: second\n")

    def test_empty_artifact_and_html_escaping(self):
        self.ideas = self.ideas[:1]
        self.ideas[0]["title"] = "</script><script>alert(1)</script>"
        self.write("ara/trace/ideas.yaml", {"ideas": self.ideas})
        for file in (self.root / "ara/issues").glob("*.yaml"): file.unlink()
        data = self.validate()
        page = ara.render(self.root, data)
        self.assertNotIn("</script><script>alert", page)
        self.assertEqual(ara.counts(data)["ideas"], 0)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, text=True).stdout

    def test_history_preserves_prompts_notes_and_ids(self):
        self.git("init", "-b", "main")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "baseline")
        self.assertIn("verified", ara.history(self.root, "HEAD"))
        path = "docs/plans/issue001/ExecPlan.md"
        self.text(path, (self.root / path).read_text().replace("Original User Raw Prompts", "Rewritten prompt"))
        with self.assertRaisesRegex(ValueError, "ExecPlan history rewritten"): ara.history(self.root, "HEAD")
        self.git("restore", path)
        self.ideas[1]["title"] = "Silently revised"
        self.write("ara/trace/ideas.yaml", {"ideas": self.ideas})
        with self.assertRaisesRegex(ValueError, "revision event"): ara.history(self.root, "HEAD")

    def test_current_repository(self):
        data = ara.validate(ROOT)
        self.assertIn(ara.ROOT_ID, data["ideas"])


if __name__ == "__main__":
    unittest.main()
