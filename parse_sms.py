#!/usr/bin/env python3
"""Parse SMS Backup & Restore XML backups into CSV/JSONL + readable transcripts.

Handles plain .xml and gzipped .xml.gz files of any size (streaming parse),
merges multiple overlapping backups, and dedupes identical messages.

Usage:
    python3 parse_sms.py -o output_dir backup1.xml backup2.xml.gz ...

Outputs in output_dir:
    all_messages.csv / all_messages.jsonl   one row per unique message
    transcripts/<contact>.md                chronological chat log per contact
    summary_stats.md                        per-contact counts and date ranges
"""

import argparse
import csv
import gzip
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import iterparse

# type / msg_box values per SMS Backup & Restore docs
SMS_DIRECTION = {"1": "received", "2": "sent", "3": "draft", "4": "outbox",
                 "5": "failed", "6": "queued"}
MMS_DIRECTION = {"1": "received", "2": "sent", "3": "draft", "4": "outbox"}

SKIP_PART_TYPES = ("application/smil",)


def open_backup(path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rb")
    return open(path, "rb")


def norm_number(addr):
    """Normalize a phone number so the same contact merges across files."""
    if not addr:
        return ""
    digits = re.sub(r"\D", "", addr)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits or addr.strip()


def epoch_ms_to_iso(ms):
    try:
        return datetime.fromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, OSError):
        return ""


def parse_file(path, seen, messages, stats):
    """Stream one backup file, appending unique messages to `messages`."""
    total = dupes = 0
    with open_backup(path) as fh:
        context = iterparse(fh, events=("start", "end"))
        _, root = next(context)  # grab <smses> root so we can clear it
        declared = root.get("count")
        cur_mms = None
        for event, elem in context:
            if event == "start":
                continue
            tag = elem.tag
            if tag == "sms":
                total += 1
                msg = {
                    "timestamp": epoch_ms_to_iso(elem.get("date")),
                    "epoch_ms": elem.get("date"),
                    "contact": elem.get("contact_name") or "",
                    "number": norm_number(elem.get("address")),
                    "direction": SMS_DIRECTION.get(elem.get("type"), elem.get("type")),
                    "kind": "sms",
                    "body": elem.get("body") or "",
                    "attachments": "",
                    "source": Path(path).name,
                }
                add_message(msg, seen, messages)
                elem.clear()
            elif tag == "mms":
                total += 1
                texts, attachments = [], []
                sender_addr = ""
                for part in elem.iter("part"):
                    ct = (part.get("ct") or "").lower()
                    if ct in SKIP_PART_TYPES:
                        continue
                    if ct.startswith("text/"):
                        t = part.get("text") or ""
                        if t and t != "null":
                            texts.append(t)
                    else:
                        attachments.append(ct or "unknown")
                for addr in elem.iter("addr"):
                    if addr.get("type") == "137":  # 137 = sender
                        sender_addr = addr.get("address") or ""
                address = elem.get("address") or ""
                is_group = "~" in address
                msg = {
                    "timestamp": epoch_ms_to_iso(elem.get("date")),
                    "epoch_ms": elem.get("date"),
                    "contact": elem.get("contact_name") or "",
                    "number": norm_number(address if not is_group else address),
                    "direction": MMS_DIRECTION.get(elem.get("msg_box"),
                                                   elem.get("msg_box")),
                    "kind": "mms-group" if is_group else "mms",
                    "body": "\n".join(texts),
                    "attachments": ", ".join(f"[{a}]" for a in attachments),
                    "source": Path(path).name,
                }
                if is_group:
                    msg["group_sender"] = norm_number(sender_addr)
                add_message(msg, seen, messages)
                elem.clear()
            root.clear()
    stats[Path(path).name] = {"declared": declared, "parsed": total}
    return total


def add_message(msg, seen, messages):
    key = (msg["number"], msg["epoch_ms"], msg["direction"], msg["body"],
           msg["attachments"])
    if key in seen:
        return False
    seen.add(key)
    messages.append(msg)
    return True


def contact_label(msg):
    name = (msg["contact"] or "").strip()
    if name and name.lower() != "(unknown)":
        return name
    return msg["number"] or "unknown"


def safe_filename(label):
    s = re.sub(r"[^\w\s\-,&]", "", label).strip()
    s = re.sub(r"\s+", "_", s)
    return s[:80] or "unknown"


def write_outputs(messages, outdir):
    outdir = Path(outdir)
    (outdir / "transcripts").mkdir(parents=True, exist_ok=True)
    messages.sort(key=lambda m: int(m["epoch_ms"] or 0))

    fields = ["timestamp", "contact", "number", "direction", "kind", "body",
              "attachments", "source"]
    with open(outdir / "all_messages.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(messages)
    with open(outdir / "all_messages.jsonl", "w", encoding="utf-8") as f:
        for m in messages:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    by_contact = defaultdict(list)
    for m in messages:
        by_contact[contact_label(m)].append(m)

    for label, msgs in by_contact.items():
        path = outdir / "transcripts" / f"{safe_filename(label)}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {label}\n\n")
            f.write(f"{len(msgs)} messages, "
                    f"{msgs[0]['timestamp'][:10]} to {msgs[-1]['timestamp'][:10]}\n")
            last_day = None
            for m in msgs:
                day = m["timestamp"][:10]
                if day != last_day:
                    f.write(f"\n## {day}\n\n")
                    last_day = day
                who = "Me" if m["direction"] == "sent" else label
                if m["kind"] == "mms-group" and m["direction"] != "sent":
                    who = m.get("group_sender") or label
                time = m["timestamp"][11:16]
                body = (m["body"] or "").strip()
                extra = f" {m['attachments']}" if m["attachments"] else ""
                f.write(f"- `{time}` **{who}:** {body}{extra}\n")

    with open(outdir / "summary_stats.md", "w", encoding="utf-8") as f:
        f.write("# SMS backup summary\n\n")
        f.write(f"Total unique messages: **{len(messages)}**\n\n")
        f.write("| Contact | Messages | Sent | Received | First | Last |\n")
        f.write("|---|---|---|---|---|---|\n")
        for label, msgs in sorted(by_contact.items(),
                                  key=lambda kv: -len(kv[1])):
            sent = sum(1 for m in msgs if m["direction"] == "sent")
            recv = sum(1 for m in msgs if m["direction"] == "received")
            f.write(f"| {label} | {len(msgs)} | {sent} | {recv} "
                    f"| {msgs[0]['timestamp'][:10]} "
                    f"| {msgs[-1]['timestamp'][:10]} |\n")

    return by_contact


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", help=".xml or .xml.gz backup files")
    ap.add_argument("-o", "--outdir", default="output")
    args = ap.parse_args()

    seen, messages, stats = set(), [], {}
    for path in args.files:
        n = parse_file(path, seen, messages, stats)
        print(f"{path}: parsed {n} (declared {stats[Path(path).name]['declared']}), "
              f"unique so far {len(messages)}", file=sys.stderr)

    by_contact = write_outputs(messages, args.outdir)
    print(f"\n{len(messages)} unique messages across {len(by_contact)} "
          f"contacts -> {args.outdir}/", file=sys.stderr)


if __name__ == "__main__":
    main()
