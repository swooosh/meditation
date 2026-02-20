#!/usr/bin/env python3
"""Generate web/render-status.js from status report + QC artifacts."""
import json
from pathlib import Path

from status_report import build_status


def load_qc(root: Path, row: dict):
    if not row.get("render_path"):
        return None
    render_path = Path(row["render_path"])
    qc_path = render_path.parent / "qc" / f"{row['id']}_qc.json"
    if not qc_path.exists():
        return None
    try:
        return json.loads(qc_path.read_text())
    except Exception:
        return None


def main():
    root = Path(__file__).resolve().parents[1]
    rows = build_status(root)

    manifest = {}
    for row in rows:
        qc = load_qc(root, row)
        manifest[row["id"]] = {
            "renderExists": bool(row["render_exists"]),
            "renderComplete": bool(row["render_complete"]),
            "qcExists": bool(qc),
            "qcPassed": bool(qc.get("qc_passed")) if qc else False,
            "qcFailedChecks": qc.get("failed_checks", []) if qc else [],
        }

    out_path = root / "web" / "render-status.js"
    out_path.write_text(
        "// Generated from tools/update_render_status.py\n"
        "const RENDER_STATUS =\n"
        + json.dumps(manifest, indent=2)
        + ";\n"
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
