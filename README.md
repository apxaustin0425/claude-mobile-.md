# claude-mobile-.md

## SMS backup parser

`parse_sms.py` converts [SMS Backup & Restore](https://synctech.com.au/sms-backup-restore/)
XML exports (plain `.xml` or gzipped `.xml.gz`, any size) into:

- `all_messages.csv` / `all_messages.jsonl` — one row per unique message
- `transcripts/<contact>.md` — a readable chronological chat log per contact
- `summary_stats.md` — per-contact message counts and date ranges

Multiple overlapping backups can be passed at once; identical messages are
deduplicated automatically. MMS text is extracted; binary attachments become
`[image/jpeg]`-style placeholders.

```bash
python3 parse_sms.py -o output sms-backup1.xml sms-backup2.xml.gz ...
```

Requires only the Python 3 standard library.
