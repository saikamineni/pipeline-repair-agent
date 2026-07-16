import shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = ROOT / "evals" / "fixtures"


def _ignore_pycache(dir_, names):
    return [n for n in names if n == "__pycache__" or n.endswith(".pyc")]


def _ignore_duckdb(dir_, names):
    return [n for n in names if n.endswith(".duckdb")]


def make_fixture(name):
    dest = FIXTURES_DIR / name / "repo"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    shutil.copytree(ROOT / "pipeline", dest / "pipeline", ignore=_ignore_pycache)
    shutil.copytree(ROOT / "tests", dest / "tests", ignore=_ignore_pycache)
    shutil.copytree(ROOT / "data", dest / "data", ignore=_ignore_duckdb)
    shutil.copy2(ROOT / "CLAUDE.md", dest / "CLAUDE.md")
    shutil.copy2(ROOT / "conftest.py", dest / "conftest.py")


def main():
    for name in sys.argv[1:]:
        make_fixture(name)
        print(f"created {FIXTURES_DIR / name / 'repo'}")


if __name__ == "__main__":
    main()
