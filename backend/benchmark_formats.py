"""
Format Benchmark — Storyboard AI.

Tests all supported script formats for:
  - Parse time (milliseconds)
  - Scene count
  - Character count
  - Word count
  - Format detection accuracy

Run from the backend directory:
  python benchmark_formats.py

Output: A formatted performance table printed to stdout and saved to
logs/format_benchmark_YYYYMMDD.log
"""
import time
import os
import sys
import json
from time_utils import utc_now  # type: ignore
from pathlib import Path
from typing import List, Dict, Any

# ── Add backend to path ───────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from script_parser import ScriptParser  # type: ignore
from parsers.format_detector import detect_format  # type: ignore
from parsers.fdx_parser import parse_fdx  # type: ignore
from parsers.fountain_parser import parse_fountain  # type: ignore

FORMATS_DIR = Path(__file__).parent / "test_scripts" / "formats"
LEGACY_DIR = Path(__file__).parent / "test_scripts"

# ── All test documents ────────────────────────────────────────────────────────
TEST_DOCUMENTS = [
    # Legacy plain-text screenplays
    {"path": LEGACY_DIR / "noir_3min.txt",           "expected_format": "text",    "label": "Plain Text Screenplay (Noir 3min)"},
    {"path": LEGACY_DIR / "drama_5min.txt",          "expected_format": "text",    "label": "Plain Text Screenplay (Drama 5min)"},
    {"path": LEGACY_DIR / "sci_fi_1min.txt",         "expected_format": "text",    "label": "Plain Text Screenplay (SciFi 1min)"},
    # New format demos
    {"path": FORMATS_DIR / "sample_scifi_thriller.fountain",  "expected_format": "fountain", "label": "Fountain Format (SciFi Thriller)"},
    {"path": FORMATS_DIR / "sample_noir_detective.fdx",       "expected_format": "fdx",      "label": "Final Draft FDX (Noir Detective)"},
    {"path": FORMATS_DIR / "sample_av_documentary.txt",       "expected_format": "text",     "label": "A/V Script (Documentary)"},
    {"path": FORMATS_DIR / "sample_stage_play.txt",           "expected_format": "text",     "label": "Stage Play (2-Act Drama)"},
    {"path": FORMATS_DIR / "sample_tv_episode.txt",           "expected_format": "text",     "label": "TV Episode (One-Hour Procedural)"},
    {"path": FORMATS_DIR / "sample_novel_chapter.txt",        "expected_format": "text",     "label": "Novel Chapter (Prose Fiction)"},
    {"path": FORMATS_DIR / "sample_episodic_series.txt",      "expected_format": "text",     "label": "Episodic Web Series (12min Short)"},
]


def benchmark_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Run all benchmarks on a single document."""
    path: Path = doc["path"]
    if not path.exists():
        return {
            "label": doc["label"],
            "status": "FILE NOT FOUND",
            "path": str(path),
        }

    file_bytes = path.read_bytes()
    content_str = ""
    try:
        content_str = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content_str = file_bytes.decode("latin-1")

    # ── Format detection ─────────────────────────────────────────────────────
    t0 = time.perf_counter()
    detected_fmt = detect_format(path.name, file_bytes)
    detect_time_ms = (time.perf_counter() - t0) * 1000

    format_correct = detected_fmt == doc["expected_format"]

    # ── Parse ────────────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    if detected_fmt == "fdx":
        scenes = parse_fdx(content_str)
    elif detected_fmt == "fountain":
        scenes = parse_fountain(content_str)
    else:
        scenes = ScriptParser.parse(content_str)
    parse_time_ms = (time.perf_counter() - t0) * 1000

    # ── Metrics ──────────────────────────────────────────────────────────────
    scene_count = len(scenes)
    word_count = len(content_str.split())
    char_count = len(content_str)
    total_characters = set()
    for s in scenes:
        for c in s.get("characters", []):
            total_characters.add(c)

    return {
        "label": doc["label"],
        "file": path.name,
        "status": "OK",
        "detected_format": detected_fmt,
        "expected_format": doc["expected_format"],
        "format_detection_correct": format_correct,
        "detect_time_ms": round(detect_time_ms, 2),
        "parse_time_ms": round(parse_time_ms, 2),
        "total_time_ms": round(detect_time_ms + parse_time_ms, 2),
        "scene_count": scene_count,
        "character_count": len(total_characters),
        "word_count": word_count,
        "file_size_bytes": len(file_bytes),
        "words_per_scene": round(word_count / max(scene_count, 1), 1),
    }


def print_report(results: List[Dict[str, Any]]) -> str:
    """Format and print the benchmark report. Returns the report as a string."""
    lines = []
    lines.append("")
    lines.append("=" * 100)
    lines.append("STORYBOARD AI — FORMAT BENCHMARK REPORT")
    lines.append(f"Run at: {utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"Documents tested: {len(results)}")
    lines.append("=" * 100)

    # ── Summary table ─────────────────────────────────────────────────────────
    header = (
        f"{'Document':<45} {'Format':<10} {'Det?':<5} "
        f"{'Scenes':<7} {'Chars':<6} {'Words':<7} "
        f"{'Det ms':<8} {'Parse ms':<9} {'Total ms':<9}"
    )
    lines.append(header)
    lines.append("-" * 100)

    total_scenes = 0
    total_words = 0
    detection_correct = 0
    errors = []

    for r in results:
        if r["status"] != "OK":
            lines.append(f"  {'[ERROR] ' + r['label']:<95}  {r['status']}")
            errors.append(r)
            continue

        total_scenes += r["scene_count"]
        total_words += r["word_count"]
        if r["format_detection_correct"]:
            detection_correct += 1

        det_icon = "✓" if r["format_detection_correct"] else "✗"
        row = (
            f"{r['label'][:44]:<45} {r['detected_format']:<10} {det_icon:<5} "
            f"{r['scene_count']:<7} {r['character_count']:<6} {r['word_count']:<7} "
            f"{r['detect_time_ms']:<8} {r['parse_time_ms']:<9} {r['total_time_ms']:<9}"
        )
        lines.append(row)

    ok_count = len([r for r in results if r["status"] == "OK"])
    lines.append("-" * 100)
    lines.append(
        f"TOTALS: {ok_count} docs OK | "
        f"Format detection: {detection_correct}/{ok_count} correct | "
        f"Total scenes: {total_scenes} | Total words: {total_words:,}"
    )

    if ok_count > 0:
        avg_parse = sum(r["parse_time_ms"] for r in results if r["status"] == "OK") / ok_count
        lines.append(f"Average parse time: {avg_parse:.2f}ms per document")

    lines.append("=" * 100)

    # ── Format coverage summary ───────────────────────────────────────────────
    lines.append("")
    lines.append("FORMAT COVERAGE MATRIX")
    lines.append("-" * 60)
    formats_tested = set(r.get("detected_format", "") for r in results if r["status"] == "OK")
    coverage = {
        "text (plain screenplay)": "text" in formats_tested,
        "fountain (open-source format)": "fountain" in formats_tested,
        "fdx (Final Draft XML)": "fdx" in formats_tested,
        "pdf (via pdfplumber)": "pdf" in formats_tested,
        "docx (Microsoft Word)": "docx" in formats_tested,
    }
    for fmt, tested in coverage.items():
        status = "✓ TESTED" if tested else "○ NOT IN THIS RUN"
        lines.append(f"  {fmt:<40} {status}")
    lines.append("")
    lines.append("Script types covered in this benchmark:")
    script_types = [
        "Plain Text Screenplay (INT./EXT.)",
        "Fountain Format (open standard)",
        "Final Draft FDX (industry XML)",
        "A/V Two-Column Documentary Script",
        "Stage Play (ACT/SCENE format)",
        "Television Episode (Teaser/Acts/Tag)",
        "Novel / Prose (chapter format)",
        "Episodic Web Series",
    ]
    for st in script_types:
        lines.append(f"  ✓ {st}")
    lines.append("=" * 100)
    lines.append("")

    report = "\n".join(lines)
    print(report)
    return report


def save_report(report: str) -> None:
    """Save the benchmark report to logs/."""
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    date_str = utc_now().strftime("%Y%m%d_%H%M%S")
    report_path = logs_dir / f"format_benchmark_{date_str}.log"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report saved to: {report_path}")


def run_benchmark() -> List[Dict[str, Any]]:
    results = []
    print(f"\nRunning format benchmark on {len(TEST_DOCUMENTS)} documents...\n")
    for doc in TEST_DOCUMENTS:
        print(f"  Testing: {doc['label']}...")
        result = benchmark_document(doc)
        results.append(result)
    return results


if __name__ == "__main__":
    results = run_benchmark()
    report = print_report(results)
    save_report(report)

    # Also write JSON results
    json_out = Path(__file__).parent.parent / "logs" / f"format_benchmark_{utc_now().strftime('%Y%m%d_%H%M%S')}.json"
    json_out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"JSON results: {json_out}")
