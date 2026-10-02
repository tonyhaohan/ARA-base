#!/usr/bin/env python3
"""ARA Base: validate, query, extract and render a two-level research artifact."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

from notes import parse_document, extract_idea, detail_fields

ROOT_ID = "I000-N00"
NODE = re.compile(r"I([0-9]+)-N([0-9]+)")
TYPES = {"question", "decision", "experiment", "dead_end", "pivot"}
STATES = {"open", "accepted", "partial", "rejected", "superseded"}
PROVENANCE = {"user", "ai-suggested", "ai-executed", "user-revised"}
CLAIM_STATES = {"hypothesis", "untested", "testing", "supported", "weakened", "refuted", "withdrawn"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    pairs = loader.construct_pairs(node, deep=deep)
    result = {}
    for key, value in pairs:
        require(isinstance(key, (str, int)), "YAML key must be a string or integer")
        require(key not in result, f"Duplicate YAML key: {key}")
        result[key] = value
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def parse_yaml(text):
    return yaml.load(text, Loader=UniqueLoader)


def local_file(root, relative):
    require(isinstance(relative, str) and relative.strip(), "Missing relative file path")
    require(not Path(relative).is_absolute(), f"Absolute path is not portable: {relative}")
    path = (root / relative.split("#", 1)[0]).resolve()
    require(path.is_relative_to(root.resolve()), f"Path escapes project: {relative}")
    require(path.is_file(), f"Missing file: {relative}")
    return path


def load_yaml(root, relative):
    return parse_yaml(local_file(root, relative).read_text(encoding="utf-8"))


def rows(root, relative, key):
    data = load_yaml(root, relative)
    require(isinstance(data, dict) and isinstance(data.get(key), list), f"{relative}: expected {key} list")
    return data[key]


def index(items, key="id"):
    result = {}
    for item in items:
        require(isinstance(item, dict), "Record must be a mapping")
        identity = item.get(key)
        require((isinstance(identity, str) and bool(identity.strip())) if key == "id" else (type(identity) is int), f"Invalid {key}")
        require(identity not in result, f"Duplicate {key}: {identity}")
        result[identity] = item
    return result


def nonempty(item, *keys):
    for key in keys:
        require(isinstance(item.get(key), str) and item[key].strip(), f"{item.get('id', item.get('issue', 'record'))}: missing {key}")


def refs(item, key, available, required=False):
    values = item.get(key, [])
    require(isinstance(values, list), f"{key} must be a list")
    require(all(isinstance(v, (str, int)) and not isinstance(v, bool) for v in values), f"{key}: invalid reference")
    require(len(values) == len(set(values)), f"{key}: duplicate reference")
    require(not required or values, f"{key} must not be empty")
    require(set(values) <= set(available), f"{key}: unresolved references {set(values) - set(available)}")
    return values


def dag(records):
    indegree = {key: 0 for key in records}
    successors = {key: [] for key in records}
    for key, item in records.items():
        for predecessor in refs(item, "depends_on", records):
            indegree[key] += 1
            successors[predecessor].append(key)
    ready = [key for key, degree in indegree.items() if degree == 0]
    order = []
    while ready:
        current = ready.pop()
        order.append(current)
        for successor in successors[current]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
    require(len(order) == len(records), "Dependency graph contains a cycle")
    return successors, order


def load(root):
    artifact = root / "ara"
    return {
        "project": load_yaml(root, "ara/project.yaml"),
        "ideas": index(rows(root, "ara/trace/ideas.yaml", "ideas")),
        "issues": index([parse_yaml(p.read_text()) for p in sorted((artifact / "issues").glob("issue*.yaml"))], "issue"),
        "claims": index(rows(root, "ara/logic/claims.yaml", "claims")),
        "observations": index(rows(root, "ara/staging/observations.yaml", "observations")),
        "evidence": index(rows(root, "ara/evidence/index.yaml", "evidence")),
        "sessions": index([parse_yaml(p.read_text()) for p in sorted((artifact / "trace/sessions").glob("*.yaml"))]),
    }


def validate(root, github=False):
    data = load(root)
    project = data["project"]
    require(isinstance(project, dict) and project.get("schema_version") == 1, "Unsupported schema_version")
    nonempty(project, "title", "repository")
    require(re.fullmatch(r"[\w.-]+/[\w.-]+", project["repository"]), "Invalid GitHub owner/repo")
    require(project.get("root") == ROOT_ID, "Expected virtual root I000-N00")
    ideas, issues = data["ideas"], data["issues"]
    claims, observations, evidence = data["claims"], data["observations"], data["evidence"]
    require(ROOT_ID in ideas, "Virtual root missing")
    virtual = ideas[ROOT_ID]
    require(virtual.get("type") == "root" and virtual.get("depends_on") == [], "Invalid virtual root")
    require(not any(k in virtual for k in ("issue", "primary_dependency", "record", "evidence")), "Virtual root cannot own research data")
    normalized = set()
    for identity, idea in ideas.items():
        require(not any(key in idea for key in ("next", "children", "also_depends_on")), f"{identity}: only forward prerequisite declarations are allowed")
        nonempty(idea, "title")
        match = NODE.fullmatch(str(identity))
        require(match is not None, f"Invalid idea ID {identity}")
        numerical = tuple(map(int, match.groups()))
        require(numerical not in normalized, f"Duplicate numerical idea ID {identity}")
        normalized.add(numerical)
        if identity == ROOT_ID:
            continue
        require(numerical[0] > 0 and numerical[1] > 0, f"Invalid real idea {identity}")
        require(type(idea.get("issue")) is int and idea["issue"] == numerical[0] and idea["issue"] in issues, f"{identity}: issue ownership mismatch")
        require(idea.get("type") in TYPES and idea.get("status") in STATES, f"{identity}: invalid type or status")
        require(idea.get("provenance") in PROVENANCE, f"{identity}: invalid provenance")
        nonempty(idea, "timestamp", "record")
        dependencies = refs(idea, "depends_on", ideas, True)
        require(ROOT_ID not in dependencies or dependencies == [ROOT_ID], f"{identity}: virtual and real dependencies cannot mix")
        require(idea.get("primary_dependency") in dependencies, f"{identity}: primary_dependency must be one of depends_on")
        proof = refs(idea, "evidence", evidence)
        if not proof:
            nonempty(idea, "evidence_note")
        if idea["status"] == "accepted" and idea["type"] in {"experiment", "decision", "pivot"}:
            require(proof, f"{identity}: accepted result lacks evidence")
        memo, _, fragment = idea["record"].partition("#")
        require(memo == issues[idea["issue"]].get("record"), f"{identity}: memo differs from Issue memo")
        require(not fragment or fragment == identity, f"{identity}: memo fragment points to another idea")
    data["successors"], _ = dag(ideas)
    dag(issues)
    branches = set()
    data["notes"] = {}
    data["common"] = {}
    data["details"] = {}
    for number, issue in issues.items():
        require(type(number) is int and number > 0, "Issue number must be positive")
        nonempty(issue, "title", "url", "branch", "summary", "record", "execplan")
        require(issue["url"] == f"https://github.com/{project['repository']}/issues/{number}", f"Issue #{number}: URL mismatch")
        require(re.fullmatch(rf"codex/issue{number}-[a-z0-9][a-z0-9-]*", issue["branch"]), f"Issue #{number}: branch naming mismatch")
        require(issue["branch"] not in branches, "Branch belongs to multiple Issues")
        branches.add(issue["branch"])
        require(issue.get("status") in {"active", "completed"} and issue.get("outcome") in {"open", "success", "partial", "failed"}, f"Issue #{number}: invalid status/outcome")
        owned = {key for key, item in ideas.items() if item.get("issue") == number}
        require(owned, f"Issue #{number}: no real ideas")
        for group in ("best_ideas", "promising_ideas"):
            entries = issue.get(group)
            require(isinstance(entries, list) and entries, f"Issue #{number}: {group} must not be empty")
            selected = index(entries)
            require(set(selected) <= owned, f"Issue #{number}: {group} contains another Issue's idea")
            for entry in selected.values():
                nonempty(entry, "reason")
        path = local_file(root, issue["record"])
        shared, sections = parse_document(path.read_text())
        require(set(sections) == owned, f"Issue #{number}: memo/DAG mismatch {set(sections) ^ owned}")
        for identity, (_, section) in sections.items():
            detail = detail_fields(section)
            needed = {"question": ("question",), "decision": ("choice", "alternatives"),
                      "experiment": ("hypothesis", "method", "result"),
                      "dead_end": ("hypothesis", "result", "failure_mode", "lesson"),
                      "pivot": ("trigger", "new_direction", "result")}[ideas[identity]["type"]]
            if ideas[identity]["status"] in {"partial", "rejected", "superseded"}:
                needed = tuple(set(needed) | {"lesson"})
            for field in needed:
                require(detail.get(field), f"{identity}: memo missing nonempty ### {field}")
            data["details"][identity] = detail
        data["common"][number] = shared
        data["notes"].update({key: shared + content for key, (_, content) in sections.items()})
        plan = local_file(root, issue["execplan"]).read_text()
        for heading in ("Goal", "User Raw Prompts", "Progress", "Next Steps", "Decisions", "Evidence and Recovery"):
            require(f"## {heading}\n" in plan, f"Issue #{number}: ExecPlan missing {heading}")
    for identity, item in evidence.items():
        require(re.fullmatch(r"E[0-9]+-[0-9]+", str(identity)), f"Invalid evidence ID {identity}")
        nonempty(item, "kind", "summary", "location", "result")
        require(item.get("raw_availability") in {"bundled", "external", "unavailable", "not_applicable"}, f"{identity}: missing raw availability")
        require(isinstance(item.get("identity"), dict) and item["identity"], f"{identity}: missing identity")
        require(isinstance(item.get("reproduction"), dict) and item["reproduction"], f"{identity}: missing reproduction entry or explanation")
        location = item["location"]
        if location.startswith("https://"):
            require(urlparse(location).hostname, f"{identity}: invalid URL")
        else:
            path = local_file(root, location)
            digest = item["identity"].get("sha256")
            require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest), f"{identity}: local evidence needs SHA256")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, f"{identity}: evidence hash mismatch")
    for identity, claim in claims.items():
        require(re.fullmatch(r"C[0-9]+-[0-9]+", str(identity)), f"Invalid claim ID {identity}")
        nonempty(claim, "statement", "conditions", "falsification")
        require(claim.get("status") in CLAIM_STATES and claim.get("provenance") in PROVENANCE | {"unknown"}, f"{identity}: invalid claim status/provenance")
        refs(claim, "evidence", evidence, claim["status"] in {"supported", "refuted"})
        refs(claim, "observations", observations)
        refs(claim, "depends_on", claims)
    dag(claims)
    for identity, observation in observations.items():
        require(str(identity).startswith("O"), f"Invalid observation ID {identity}")
        nonempty(observation, "timestamp", "text", "context", "promotion_condition")
        require(observation.get("issue") in issues and observation.get("provenance") in PROVENANCE | {"unknown"}, f"{identity}: invalid observation ownership/provenance")
        refs(observation, "bound_to", set(ideas) - {ROOT_ID}, True)
    objects = set(ideas) | set(claims) | set(observations) | set(evidence)
    require(len(objects) == len(ideas) + len(claims) + len(observations) + len(evidence), "Record identities collide across layers")
    events = []
    for session in data["sessions"].values():
        nonempty(session, "timestamp", "summary")
        refs(session, "issues", issues, True)
        require(isinstance(session.get("events"), list) and session["events"], "Session needs events")
        events.extend(session["events"])
    events = index(events)
    require(not set(events) & objects, "Event ID collides with a record")
    for identity, event in events.items():
        nonempty(event, "timestamp", "rationale")
        require(event.get("provenance") in PROVENANCE | {"unknown"}, f"{identity}: invalid event provenance")
        action = event.get("action")
        require(action in {"capture", "crystallize", "revise", "conflict", "resolve", "withdraw", "import"}, f"{identity}: invalid event action")
        for key in ("from", "to", "refs"):
            refs(event, key, objects | set(events))
        refs(event, "evidence", evidence)
        if action == "crystallize":
            refs(event, "from", observations, True)
            refs(event, "to", set(claims) | (set(ideas) - {ROOT_ID}), True)
            require(event.get("trigger") in {"user_affirmation", "empirical_resolution", "artifact_commitment", "topic_abandonment"}, "Crystallization needs a closure trigger")
        if action == "revise":
            require(event.get("subject") in set(claims) | set(ideas), "Revision has no subject")
            require(isinstance(event.get("before"), dict) and isinstance(event.get("after"), dict), "Revision needs complete before/after mappings")
        if action == "conflict":
            require(len(event.get("refs", [])) >= 2, "Conflict needs both referenced sides")
        if action == "resolve":
            require(event.get("conflict") in events and events[event["conflict"]]["action"] == "conflict", "Resolution must reference a conflict event")
    data["events"] = events
    if github:
        for number, issue in issues.items():
            command = ["gh", "issue", "develop", str(number), "--repo", project["repository"], "--list"]
            linked = subprocess.run(command, check=True, capture_output=True, text=True).stdout
            links = [line for line in linked.splitlines() if line.strip()]
            require(len(links) == 1 and issue["branch"] in links[0], f"Issue #{number}: expected exactly one actual linked branch; got {linked!r}")
            subprocess.run(["gh", "api", f"repos/{project['repository']}/branches/{issue['branch']}"], check=True, capture_output=True, text=True)
    return data


def counts(data):
    return {"issues": len(data["issues"]), "ideas": len(data["ideas"]) - 1,
            "dependencies": sum(len(i["depends_on"]) for i in data["ideas"].values()),
            "claims": len(data["claims"]), "observations": len(data["observations"]),
            "evidence": len(data["evidence"]), "sessions": len(data["sessions"]),
            "raw_not_bundled": sum(e["raw_availability"] in {"external", "unavailable"} for e in data["evidence"].values())}


def render(root, data):
    payload = {key: data[key] for key in ("project", "ideas", "issues", "notes", "claims", "observations", "evidence", "events", "successors", "details")}
    payload["counts"] = counts(data)
    serialized = json.dumps(payload, ensure_ascii=False, default=str).replace("<", "\\u003c")
    template = Path(__file__).with_name("viewer.html").read_text(encoding="utf-8")
    return template.replace("__ARA_DATA__", serialized)


def git_text(root, base, path):
    result = subprocess.run(["git", "show", f"{base}:{path}"], cwd=root, capture_output=True, text=True)
    require(result.returncode == 0, f"Cannot read historical file {base}:{path}")
    return result.stdout


def sections(text):
    parts = re.split(r"(?m)^## (.+)\n", text)
    return dict(zip(parts[1::2], parts[2::2]))


def history(root, base):
    subprocess.run(["git", "rev-parse", "--verify", f"{base}^{{commit}}"], cwd=root, check=True, capture_output=True)
    current = validate(root)
    listing = subprocess.run(["git", "ls-tree", "-r", "--name-only", base], cwd=root, check=True, capture_output=True, text=True).stdout.splitlines()
    old_events = {}
    for path in listing:
        if path.startswith("ara/trace/sessions/") and path.endswith(".yaml"):
            old = parse_yaml(git_text(root, base, path))
            new = load_yaml(root, path)
            require(new.get("events", [])[:len(old["events"])] == old["events"], f"Session history rewritten: {path}")
            old_events.update(index(old["events"]))
        elif path == "ara/staging/observations.yaml":
            old = index(parse_yaml(git_text(root, base, path))["observations"])
            require(all(current["observations"].get(k) == v for k, v in old.items()), "Original observation rewritten or removed")
        elif path.startswith("ara/issues/") and path.endswith(".md"):
            shared, old = parse_document(git_text(root, base, path))
            new_shared, new = parse_document(local_file(root, path).read_text())
            require(new_shared.startswith(shared), f"Shared conditions rewritten: {path}")
            require(all(k in new and new[k][1].startswith(v[1]) for k, v in old.items()), f"Historical idea notes rewritten: {path}")
        elif path.startswith("docs/plans/") and path.endswith("/ExecPlan.md"):
            old = sections(git_text(root, base, path))
            new = sections(local_file(root, path).read_text())
            require(all(k == "Goal" or k in new and new[k].startswith(v) for k, v in old.items()), f"ExecPlan history rewritten: {path}")
    revisions = [e for key, e in current["events"].items() if key not in old_events and e["action"] == "revise"]
    for path, key in (("ara/trace/ideas.yaml", "ideas"), ("ara/logic/claims.yaml", "claims")):
        if path not in listing:
            continue
        old = index(parse_yaml(git_text(root, base, path))[key])
        for identity, before in old.items():
            require(identity in current[key], f"Historical identity removed: {identity}")
            after = current[key][identity]
            if after != before:
                require(any(e.get("subject") == identity and e["before"] == before and e["after"] == after for e in revisions), f"{identity}: change requires a new exact before/after revision event")
    return "Append-only history verified against " + base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("validate")
    check.add_argument("--github", action="store_true")
    commands.add_parser("issues")
    issue_query = commands.add_parser("issue")
    issue_query.add_argument("number", type=int)
    listing = commands.add_parser("ideas")
    listing.add_argument("--issue", type=int)
    read = commands.add_parser("read")
    read.add_argument("id")
    info = commands.add_parser("show")
    info.add_argument("id")
    paint = commands.add_parser("render")
    paint.add_argument("--check", action="store_true")
    previous = commands.add_parser("history")
    previous.add_argument("--base", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        data = validate(root, getattr(args, "github", False))
        if args.command == "validate":
            print(json.dumps(counts(data), ensure_ascii=False, indent=2))
        elif args.command == "issues":
            for number, item in data["issues"].items():
                print(f"#{number}\t{item['title']}\t{item['outcome']}")
        elif args.command == "issue":
            require(args.number in data["issues"], f"Unknown Issue #{args.number}")
            print(yaml.safe_dump(data["issues"][args.number], allow_unicode=True, sort_keys=False), end="")
        elif args.command == "ideas":
            for key, item in data["ideas"].items():
                if key != ROOT_ID and (args.issue is None or item["issue"] == args.issue):
                    print(f"{key}\t{item['type']}\t{item['status']}\t{item['title']}")
        elif args.command == "read":
            require(args.id in data["notes"], f"No real idea memo: {args.id}")
            print(data["notes"][args.id], end="")
        elif args.command == "show":
            found = next((data[key][args.id] for key in ("ideas", "claims", "observations", "evidence", "events") if args.id in data[key]), None)
            require(found is not None, f"Unknown ID {args.id}")
            result = {"record": found}
            if args.id in data["ideas"]:
                result["successors"] = data["successors"][args.id]
            result["events"] = [e for e in data["events"].values() if args.id in e.get("from", []) + e.get("to", []) + e.get("refs", []) or e.get("subject") == args.id]
            print(yaml.safe_dump(result, allow_unicode=True, sort_keys=False), end="")
        elif args.command == "render":
            output = root / "ara/views/index.html"
            page = render(root, data)
            if args.check:
                require(output.is_file() and output.read_text() == page, "Generated HTML is stale; run render")
                print("HTML is current")
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(page, encoding="utf-8")
                print(output)
        else:
            print(history(root, args.base))
    except (ValueError, OSError, yaml.YAMLError, subprocess.CalledProcessError) as exc:
        message = (exc.stderr or str(exc)).strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        parser.exit(1, f"ARA error: {message}\n")


if __name__ == "__main__":
    main()
