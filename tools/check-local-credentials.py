"""Detect generated local credentials in candidate Git files without printing values."""

import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
values: set[str] = set()
for name in ("database-runtime.json", "dev-accounts.json", "test-accounts.json"):
    file = root / ".tools" / name
    if file.exists():
        values.update(value for value in json.loads(file.read_text()).values()
                      if isinstance(value, str) and len(value) >= 16)
files = subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root, text=True,
).splitlines()
found = []
for name in files:
    path = root / name
    if path.is_file():
        data = path.read_bytes()
        if any(value.encode() in data for value in values):
            found.append(name)
if found:
    raise SystemExit("Generated credential material detected in: " + ", ".join(found))
print(f"No generated local credential values found in {len(files)} candidate Git files.")
