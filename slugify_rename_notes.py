import re, pathlib, unicodedata

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+","-", s).strip("-").lower()
    return s or "untitled"

for p in pathlib.Path(".").glob("New Text Document (*.txt)"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    first = next((l.strip() for l in text.splitlines() if l.strip()), p.stem)
    new = p.with_name(f"{slugify(first)[:80]}.md")
    if not new.exists():
        new.write_text(f"---\ntitle: {first}\n---\n\n{text}", encoding="utf-8")
        p.unlink()
        print(f"{p.name} -> {new.name}")
