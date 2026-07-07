import subprocess, pathlib


EXCLUDE = {".venv", "__pycache__", ".git", "node_modules", ".pytest_cache"}
def read_file(path: str) -> str:
    text = pathlib.Path(path).read_text()
    return text if len(text) <= 8000 else text[:8000] + f"\n...[truncated, {len(text)} chars total]"

def write_file(path: str, content: str) -> str:
    pathlib.Path(path).write_text(content)
    return f"wrote {path} ({len(content)} chars)"


def list_files(directory: str = ".") -> str:
    paths = [str(p) for p in pathlib.Path(directory).rglob("*.py")
             if not EXCLUDE & set(p.parts)]
    return "\n".join(paths[:200])


def grep(pattern: str, directory: str = ".") -> str:
    r = subprocess.run(["grep", "-rn", pattern, directory],
                       capture_output=True, text=True)
    return r.stdout[:  1500] or "no matches"

def run_tests() -> str:
    r = subprocess.run(["pytest", "-x", "-q"], capture_output=True, text=True)
    return (r.stdout + r.stderr)[-1500:]

TOOL_IMPLS = {f.__name__: f for f in [read_file, write_file, list_files, grep, run_tests]}

TOOLS = [
 {"name":"read_file","description":"Read a file's contents",
  "input_schema":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}},
 {"name":"write_file","description":"Overwrite a file with new content",
  "input_schema":{"type":"object","properties":{"path":{"type":"string"},
   "content":{"type":"string"}},"required":["path","content"]}},
 {"name":"list_files","description":"List .py files recursively",
  "input_schema":{"type":"object","properties":{"directory":{"type":"string"}}}},
 {"name":"grep","description":"Search files for a regex/pattern",
  "input_schema":{"type":"object","properties":{"pattern":{"type":"string"},
   "directory":{"type":"string"}},"required":["pattern"]}},
 {"name":"run_tests","description":"Run pytest and return output tail",
  "input_schema":{"type":"object","properties":{}}},
]