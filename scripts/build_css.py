"""Build the single production stylesheet from maintainable source modules."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PARTS = ("core.css", "components.css", "pages.css", "responsive.css")
bundle = "".join((ROOT / "styles" / name).read_text(encoding="utf-8") for name in PARTS)
target = ROOT / "styles.css"

if "--check" in sys.argv:
    if not target.is_file() or target.read_text(encoding="utf-8") != bundle:
        raise SystemExit("styles.css is stale; run python3 scripts/build_css.py")
    print("PASS: CSS bundle matches source modules")
else:
    target.write_text(bundle, encoding="utf-8")
    print("Built styles.css")
