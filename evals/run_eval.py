import json, shutil, subprocess, time, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))  # repo root, so `agent` resolves
from agent import tools as agent_tools
from agent.loop import run_agent

FIXTURES = pathlib.Path("evals/fixtures")
RUNS = pathlib.Path("evals/results")

def score_fixture(fx: pathlib.Path, run_dir: pathlib.Path) -> dict:
    work = pathlib.Path("/tmp/eval") / fx.name          # per-fixture, no clobbering
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(fx / "repo", work)

    t0 = time.time()
    agent_tools.CWD = str(work)
    result = run_agent(f"The pipeline in {work} is failing tests. Fix it.")
    passed = subprocess.run(["pytest", "-q"], cwd=work).returncode == 0
    # anti-cheat: golden tests + schemas must be byte-identical
    tampered = any((fx/"repo"/p).read_bytes() != (work/p).read_bytes() 
                   for p in ["tests/test_pipeline.py", "pipeline/schema.py"])

    # --- persist the artifacts BEFORE anything is destroyed ---
    out = run_dir / fx.name
    out.mkdir(parents=True, exist_ok=True)

    patch = subprocess.run(["diff", "-ru", str(fx/"repo"), str(work)], capture_output=True, text=True).stdout
    
    (out / "fix.patch").write_text(patch)
    
    (out / "transcript.json").write_text(json.dumps(_serialize(result["messages"]), indent=2))

    return {"fixture": fx.name, "resolved": passed and not tampered,
            "tampered": tampered, "hit_cap": not result["done"],
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

if __name__ == "__main__":
    run_dir = RUNS / time.strftime("%Y%m%d_%H%M%S")   # second-resolution: no collisions
    run_dir.mkdir(parents=True)
    rows = [score_fixture(fx, run_dir) for fx in sorted(FIXTURES.iterdir())]
    (run_dir / "summary.json").write_text(json.dumps(rows, indent=2))
    print(f"resolution: {sum(r['resolved'] for r in rows)}/{len(rows)} → {run_dir}")