import hashlib, json, shutil, subprocess, time, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # repo root, so `agent` resolves
from agent import tools as agent_tools
from agent.loop import run_agent

FIXTURES = pathlib.Path("evals/fixtures")
RUNS = pathlib.Path("evals/results")
HISTORY = RUNS / "history.jsonl"

MUTABLE = {"pipeline/extract.py", "pipeline/transform.py", "pipeline/load.py"}

def snapshot(root: pathlib.Path) -> dict[str, str]:
    EXCLUDE = {".venv", "__pycache__", ".git", ".pytest_cache"}
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file() and not EXCLUDE & set(p.parts)
    }

def audit(before: dict, after: dict) -> dict:
    modified = [p for p in before if p in after and before[p] != after[p]]
    return {
        "created":  sorted(set(after) - set(before)),
        "deleted":  sorted(set(before) - set(after)),
        "modified_allowed":   sorted(p for p in modified if p in MUTABLE),
        "modified_protected": sorted(p for p in modified if p not in MUTABLE),
    }

def score_fixture(fx: pathlib.Path, run_dir: pathlib.Path) -> dict:
    work = pathlib.Path("/tmp/eval") / fx.name          # per-fixture, no clobbering
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(fx / "repo", work)

    before = snapshot(fx / "repo")
    t0 = time.time()
    agent_tools.CWD = str(work)
    result = run_agent(f"The pipeline in {work} is failing tests. Fix it.")
    passed = subprocess.run(["pytest", "-q"], cwd=work).returncode == 0
    after = snapshot(work)

    # anti-cheat: only pipeline/{extract,transform,load}.py may change
    a = audit(before, after)
    changed = a["modified_protected"] + a["created"] + a["deleted"]
    tampered = bool(changed)

    # --- persist the artifacts BEFORE anything is destroyed ---
    out = run_dir / fx.name
    out.mkdir(parents=True, exist_ok=True)

    patch = subprocess.run(["diff", "-ru", str(fx/"repo"), str(work)], capture_output=True, text=True).stdout

    (out / "fix.patch").write_text(patch)

    (out / "transcript.json").write_text(json.dumps(_serialize(result["messages"]), indent=2))

    return {"fixture": fx.name, "resolved": passed and not tampered,
            "tests_passed": passed,          # did pytest go green?
            "tampered": tampered,            # did it cheat?
            "tampered_files": changed,       # WHICH file — you need this
            "audit": a,                      # full forensics, cheap to store
            "hit_cap": not result["done"],
            "iters": result["iters"], "seconds": round(time.time()-t0, 1)}

def _serialize(messages):
    # SDK blocks aren't JSON-native; coerce to dicts
    def coerce_block(b):
        return b if isinstance(b, dict) else b.model_dump()
    def coerce_content(c):
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            return [coerce_block(b) for b in c]
        return str(c)
    return [{"role": m["role"], "content": coerce_content(m["content"])} for m in messages]

def record_history(run_dir: pathlib.Path, rows: list, note: str) -> dict:
    resolved = sum(r["resolved"] for r in rows)
    total = len(rows)
    entry = {
        "run": run_dir.name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "note": note,
        "resolved": resolved,
        "total": total,
        "resolution_rate": round(resolved / total, 4),
    }
    with HISTORY.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

if __name__ == "__main__":
    note = sys.argv[1] if len(sys.argv) > 1 else ""   # e.g. python evals/run_eval.py "fixed run_tests cwd scoping"
    run_dir = RUNS / time.strftime("%Y%m%d_%H%M%S")   # second-resolution: no collisions
    run_dir.mkdir(parents=True)
    rows = [score_fixture(fx, run_dir) for fx in sorted(FIXTURES.iterdir())]
    (run_dir / "summary.json").write_text(json.dumps(rows, indent=2))
    entry = record_history(run_dir, rows, note)
    prior = HISTORY.read_text().splitlines()[:-1]   # exclude the entry we just wrote
    trend = f" (prev: {json.loads(prior[-1])['resolution_rate']:.0%})" if prior else ""
    print(f"resolution: {entry['resolved']}/{entry['total']} ({entry['resolution_rate']:.0%}){trend} → {run_dir}")