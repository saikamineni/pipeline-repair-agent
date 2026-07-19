import shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = ROOT / "evals" / "fixtures"


def _ignore_pycache(dir_, names):
    return [n for n in names if n == "__pycache__" or n.endswith(".pyc") or n == ".DS_Store"]


def _ignore_non_csv(dir_, names):
    # data/ is committed static CSVs only (orders.csv, customers.csv) --
    # evals/make_data.py is the one-time generator and is never part of the fixture surface.
    return [n for n in names if not n.endswith(".csv")]


def make_fixture(name):
    dest = FIXTURES_DIR / name / "repo"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    shutil.copytree(ROOT / "pipeline", dest / "pipeline", ignore=_ignore_pycache)
    shutil.copytree(ROOT / "tests", dest / "tests", ignore=_ignore_pycache)
    shutil.copytree(ROOT / "data", dest / "data", ignore=_ignore_non_csv)
    shutil.copy2(ROOT / "CLAUDE.md", dest / "CLAUDE.md")
    shutil.copy2(ROOT / "conftest.py", dest / "conftest.py")
    shutil.copy2(ROOT / "pytest.ini", dest / "pytest.ini")


def main():
    for name in sys.argv[1:]:
        make_fixture(name)
        print(f"created {FIXTURES_DIR / name / 'repo'}")


if __name__ == "__main__":
    main()
