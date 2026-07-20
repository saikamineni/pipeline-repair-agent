import sys
from pathlib import Path

# Presence of this file puts the repo root on sys.path so `import pipeline` resolves
# when tests are run via bare `pytest` (not just `python -m pytest`).
sys.path.insert(0, str(Path(__file__).parent))