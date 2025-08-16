import os
import pathlib
import datetime

SUMMARY_LENGTH = 500  # Characters to show for file summary

def summarize_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read(SUMMARY_LENGTH)
        return f"First 500 chars: {text.replace(chr(10),' ')[:100]}..."
    except Exception as e:
        return f"Error reading: {e}"

def scan_repo(repo_path):
    file_index = []
    for path, dirs, files in os.walk(repo_path):
        for name in files:
            fpath = os.path.join(path, name)
            rel = os.path.relpath(fpath, repo_path)
            stat = os.stat(fpath)
            info = {
                'path': rel,
                'size': stat.st_size,
                'last_modified': datetime.datetime.utcfromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'summary': '',
            }
            ext = pathlib.Path(name).suffix.lower()
            if ext in ['.md', '.txt', '.py', '.ipynb', '.nb', '.m', '.tex']:
                info['summary'] = summarize_file(fpath)
            file_index.append(info)
    return file_index

def write_repo_index(file_index, repo_name, output='LUFT_Repo_Index.md'):
    with open(output, 'w', encoding='utf-8') as f:
        f.write(f"# {repo_name} — LUFT Repo Index\n\n")
        f.write("**Generated on:** {}\n\n".format(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
        f.write("| Path | Size (bytes) | Last Modified | Summary |\n")
        f.write("|------|--------------|---------------|---------|\n")
        for entry in sorted(file_index, key=lambda d: d['path']):
            f.write(f"| [{entry['path']}]({entry['path']}) | {entry['size']} | {entry['last_modified']} | {entry['summary']} |\n")

def write_master_index(repo_summaries, output='LUFT_Master_MultiRepo_Index.md'):
    with open(output, 'w', encoding='utf-8') as f:
        f.write("# LUFT Project — Multi-Repo Master Index\n\n")
        f.write("**Generated on:** {}\n\n".format(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
        f.write("| Repo Name | Index Link | File Count | Notable Files |\n")
        f.write("|-----------|------------|------------|---------------|\n")
        for summary in repo_summaries:
            notable = ', '.join(summary['notable_files'][:3])
            f.write(f"| {summary['repo_name']} | [{summary['index_path']}]({summary['index_path']}) | {summary['file_count']} | {notable} |\n")

def main():
    # List your repo directories here
    repo_dirs = [
        "Reality-based-Space-and-its-functionality",
        "Unification-Physics-and-Testing-LUFT",
        "LUFT-CLINE",
        "CarlDean-ClineSr2",
        "UFT-Continuum-Project",
        "May-2025-",
        "Chronological-Craft-Inventions-LUFT",
        "LUFT-WinSPC-Data",
        "LUFT-Unified-Field-Project",
        "Lattice-Unified-Field-Theory-L.U.F.T",
        "LUFT_Recordings",
        # Add more as needed
    ]
    repo_summaries = []
    for repo in repo_dirs:
        if not os.path.exists(repo):
            print(f"Repo not found: {repo}")
            continue
        file_index = scan_repo(repo)
        repo_index_path = os.path.join(repo, "LUFT_Repo_Index.md")
        write_repo_index(file_index, repo, output=repo_index_path)
        repo_summaries.append({
            'repo_name': repo,
            'index_path': repo_index_path,
            'file_count': len(file_index),
            'notable_files': [entry['path'] for entry in file_index[:5]],
        })
    write_master_index(repo_summaries)
    print("Multi-repo master index written to LUFT_Master_MultiRepo_Index.md")

if __name__ == '__main__':
    main()
