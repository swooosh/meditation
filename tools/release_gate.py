#!/usr/bin/env python3
"""Single-command release gate for specs, renders, narration, and QC."""
import argparse
import json
from pathlib import Path

from status_report import build_status
from validate_specs import validate_spec
from validate_narration import validate_one as validate_narration_one


def load_qc_for_row(row):
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
    parser = argparse.ArgumentParser(description="Run release gate checks across the protocol library.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    parser.add_argument("--strict-spec", action="store_true", help="Treat spec warnings as gate failures.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    specs = sorted(root.glob("protocols/*/specs/*.yaml"))
    rows = build_status(root)

    spec_errors = []
    spec_warnings = []
    for spec in specs:
        errors, warnings = validate_spec(spec)
        rel = str(spec.relative_to(root))
        for err in errors:
            spec_errors.append({"spec": rel, "error": err})
        for warning in warnings:
            spec_warnings.append({"spec": rel, "warning": warning})

    missing_narration = [r["id"] for r in rows if not r.get("narration_exists")]
    narration_errors = []
    narration_warnings = []
    for spec in specs:
        pid, family, errs, warns = validate_narration_one(root, spec)
        for e in errs:
            narration_errors.append({"id": pid, "family": family, "error": e})
        for w in warns:
            narration_warnings.append({"id": pid, "family": family, "warning": w})

    incomplete_renders = [r["id"] for r in rows if not r.get("render_complete")]
    qc_missing = []
    qc_failed = []
    for row in rows:
        qc = load_qc_for_row(row)
        if qc is None:
            qc_missing.append(row["id"])
            continue
        if not qc.get("qc_passed", False):
            qc_failed.append({"id": row["id"], "failed_checks": qc.get("failed_checks", [])})

    gate_failures = []
    if spec_errors:
        gate_failures.append("spec_errors")
    if args.strict_spec and spec_warnings:
        gate_failures.append("spec_warnings")
    if missing_narration:
        gate_failures.append("missing_narration")
    if narration_errors:
        gate_failures.append("narration_errors")
    if incomplete_renders:
        gate_failures.append("incomplete_renders")
    if qc_missing:
        gate_failures.append("qc_missing")
    if qc_failed:
        gate_failures.append("qc_failed")

    payload = {
        "spec_count": len(specs),
        "protocol_count": len(rows),
        "spec_errors": spec_errors,
        "spec_warnings": spec_warnings,
        "missing_narration": missing_narration,
        "narration_errors": narration_errors,
        "narration_warnings": narration_warnings,
        "incomplete_renders": incomplete_renders,
        "qc_missing": qc_missing,
        "qc_failed": qc_failed,
        "gate_passed": len(gate_failures) == 0,
        "gate_failures": gate_failures,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Release Gate")
        print("=" * 60)
        print(f"Specs: {payload['spec_count']}")
        print(f"Protocols: {payload['protocol_count']}")
        print(f"Spec errors: {len(spec_errors)}")
        print(f"Spec warnings: {len(spec_warnings)}")
        print(f"Missing narration: {len(missing_narration)}")
        print(f"Narration errors: {len(narration_errors)}")
        print(f"Narration warnings: {len(narration_warnings)}")
        print(f"Incomplete renders: {len(incomplete_renders)}")
        print(f"QC missing: {len(qc_missing)}")
        print(f"QC failed: {len(qc_failed)}")
        print(f"Gate passed: {payload['gate_passed']}")
        if gate_failures:
            print(f"Failed checks: {', '.join(gate_failures)}")
        if qc_failed:
            for item in qc_failed:
                print(f"- QC FAIL {item['id']}: {', '.join(item['failed_checks'])}")
        if narration_errors:
            for item in narration_errors[:20]:
                print(f"- NARRATION ERROR {item['id']}: {item['error']}")

    if not payload["gate_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
