import os, re, pathlib, datetime

ROOT = pathlib.Path(".")
OUT = ROOT / "INDEX.md"

def summarize_text(path, n=3):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f.readlines()[:50] if l.strip()]
        title = lines[0][:120] if lines else path.name
        preview = " ".join(lines[1:n+1])[:240]
        return title, preview
    except Exception:
        return path.name, ""

def classify(path):
    ext = path.suffix.lower()
    if ext in {".py"}: return "Code"
    if ext in {".ipynb"}: return "Notebooks"
    if ext in {".md"}: return "Docs"
    if ext in {".txt"}: return "Notes"
    if ext in {".wav",".flac",".mp3"}: return "Audio"
    if ext in {".nb",".wl"}: return "Mathematica"
    return "Other"

files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
groups = {}
for p in files:
    groups.setdefault(classify(p), []).append(p)

with open(OUT, "w", encoding="utf-8") as out:
    out.write(f"# Repository Index\n\n")
    out.write(f"- Generated: {datetime.datetime.utcnow().isoformat()}Z\n")
    out.write(f"- Total files: {len(files)}\n\n")
    for g in sorted(groups):
        out.write(f"## {g} ({len(groups[g])})\n\n")
        for p in sorted(groups[g], key=lambda x: x.as_posix()):
            rel = p.as_posix()
            if p.suffix.lower() in {".txt",".md"}:
                title, preview = summarize_text(p)
                out.write(f"- **{title}** — [{rel}]({rel})\n  - {preview}\n")
            else:
                out.write(f"- **{p.name}** — [{rel}]({rel})\n")
        out.write("\n")
print(f"Wrote {OUT}")
