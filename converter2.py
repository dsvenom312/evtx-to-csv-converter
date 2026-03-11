"""
Convert multiple .evtx (Windows Event Log) files into a single .csv file.

Requirements:
    pip install python-evtx

Usage:
    python evtx_to_csv.py                          # auto-discovers all .evtx in current folder
    python evtx_to_csv.py C:/logs output.csv       # custom input folder and output file
    python evtx_to_csv.py C:/logs/a.evtx C:/logs/b.evtx --output merged.csv
"""

import csv
import sys
import glob
import os
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime

try:
    import Evtx.Evtx as evtx
    import Evtx.Views as e_views
except ImportError:
    print("ERROR: 'python-evtx' is not installed.")
    print("Run:  pip install python-evtx")
    sys.exit(1)


# ── Namespace used in Windows Event XML ────────────────────────────────────────
NS = "http://schemas.microsoft.com/win/2004/08/events/event"


def parse_record(record):
    """Parse a single EVTX record into a flat dictionary."""
    try:
        xml_str = e_views.evtx_record_xml_view(record)
        root = ET.fromstring(xml_str)
    except Exception:
        return None

    def find(tag):
        el = root.find(f".//{{{NS}}}{tag}")
        return el.text if el is not None else ""

    def attr(tag, attribute):
        el = root.find(f".//{{{NS}}}{tag}")
        return el.attrib.get(attribute, "") if el is not None else ""

    # EventData — collect all named Data fields
    event_data = {}
    for data in root.findall(f".//{{{NS}}}Data"):
        name = data.attrib.get("Name", "")
        value = data.text or ""
        if name:
            event_data[f"Data_{name}"] = value

    row = {
        "TimeCreated":    attr("TimeCreated", "SystemTime"),
        "EventID":        find("EventID"),
        "Level":          find("Level"),
        "Task":           find("Task"),
        "Opcode":         find("Opcode"),
        "Keywords":       find("Keywords"),
        "Channel":        find("Channel"),
        "Computer":       find("Computer"),
        "ProcessID":      attr("Execution", "ProcessID"),
        "ThreadID":       attr("Execution", "ThreadID"),
        "RecordID":       find("EventRecordID"),
        "ProviderName":   attr("Provider", "Name"),
        "UserID":         attr("Security", "UserID"),
        **event_data,
    }
    return row


def evtx_to_rows(filepath):
    """Yield parsed rows from a single .evtx file."""
    print(f"  Reading: {filepath}")
    count = 0
    try:
        with evtx.Evtx(filepath) as log:
            for record in log.records():
                row = parse_record(record)
                if row:
                    row["SourceFile"] = os.path.basename(filepath)
                    yield row
                    count += 1
    except Exception as e:
        print(f"  WARNING: Could not read {filepath}: {e}")
    print(f"    → {count:,} records")


def collect_evtx_files(paths):
    """Resolve a list of paths (files or directories) to .evtx file paths."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            found = glob.glob(os.path.join(p, "**", "*.evtx"), recursive=True)
            files.extend(found)
        elif os.path.isfile(p) and p.lower().endswith(".evtx"):
            files.append(p)
        else:
            # Treat as glob pattern
            found = glob.glob(p, recursive=True)
            files.extend(f for f in found if f.lower().endswith(".evtx"))
    return sorted(set(files))


def merge_to_csv(evtx_files, output_csv):
    """Merge all EVTX records into one CSV file."""
    all_rows = []
    all_keys = []

    for filepath in evtx_files:
        for row in evtx_to_rows(filepath):
            all_rows.append(row)
            for k in row:
                if k not in all_keys:
                    all_keys.append(k)

    if not all_rows:
        print("\nNo records found. CSV not created.")
        return

    print(f"\nWriting {len(all_rows):,} records → {output_csv}")
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    size_kb = os.path.getsize(output_csv) / 1024
    print(f"Done! File size: {size_kb:,.1f} KB")


def main():
    parser = argparse.ArgumentParser(
        description="Convert multiple .evtx files into a single CSV."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="One or more .evtx files, folders, or glob patterns. "
             "Defaults to current directory.",
    )
    parser.add_argument(
        "--output", "-o",
        default=f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        help="Output CSV filename (default: events_TIMESTAMP.csv)",
    )
    args = parser.parse_args()

    evtx_files = collect_evtx_files(args.paths)

    if not evtx_files:
        print("No .evtx files found. Check your paths and try again.")
        sys.exit(1)

    print(f"Found {len(evtx_files)} .evtx file(s):")
    for f in evtx_files:
        print(f"  {f}")
    print()

    merge_to_csv(evtx_files, args.output)


if __name__ == "__main__":
    main()
