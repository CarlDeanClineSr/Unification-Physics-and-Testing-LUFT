import difflib
import datetime

INDEX = "INDEX.md"
DIFF_LOG = "INDEX_DIFF.md"
LAST_INDEX = ".INDEX_PREV.md"

def read_lines(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return [l.rstrip() for l in f]
    except Exception:
        return []

def save_lines(file, lines):
    with open(file, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines) + '\n')

def main():
    prev = read_lines(LAST_INDEX)
    curr = read_lines(INDEX)

    if not curr:
        return

    diff = list(difflib.unified_diff(prev, curr, lineterm='', fromfile='Previous INDEX.md', tofile='Current INDEX.md'))
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    if diff:
        log_entry = f"## Index Diff @ {timestamp}\n\n" + "\n".join(diff) + "\n\n"
    else:
        log_entry = f"## Index Diff @ {timestamp}\n\n(No changes)\n\n"

    # Append or create diff log
    old_log = read_lines(DIFF_LOG)
    save_lines(DIFF_LOG, old_log + [log_entry])

    # Save current as previous for next run
    save_lines(LAST_INDEX, curr)

if __name__ == "__main__":
    main()
