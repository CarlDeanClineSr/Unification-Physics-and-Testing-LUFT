import os
import pathlib
import datetime

try:
    from openai import OpenAI
    # Set your OpenAI key here if you want to use GPT-3/4 for summaries
    use_openai = True
except ImportError:
    use_openai = False

SUMMARY_LENGTH = 500  # Characters to read for summary if no AI

def summarize_file(filepath):
    try:
        if use_openai:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read(SUMMARY_LENGTH)
            # Replace with your OpenAI prompt if you have an API key
            return f"AI summary (placeholder): {text[:100]}..."
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read(SUMMARY_LENGTH)
            return f"First 500 chars: {text.replace(chr(10),' ')[:100]}..."
    except Exception as e:
        return f"Error reading: {e}"

def scan_repo(root='.'):
    file_index = []
    for path, dirs, files in os.walk(root):
        for name in files:
            fpath = os.path.join(path, name)
            rel = os.path.relpath(fpath, root)
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

def write_index(file_index, output='LUFT_Master_Index.md'):
    with open(output, 'w', encoding='utf-8') as f:
        f.write("# LUFT Project Master Index\n\n")
        f.write("**Generated on:** {}\n\n".format(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
        f.write("| Path | Size (bytes) | Last Modified | Summary |\n")
        f.write("|------|--------------|---------------|---------|\n")
        for entry in sorted(file_index, key=lambda d: d['path']):
            f.write(f"| [{entry['path']}]({entry['path']}) | {entry['size']} | {entry['last_modified']} | {entry['summary']} |\n")

if __name__ == '__main__':
    index = scan_repo('.')
    write_index(index)
    print("Master index written to LUFT_Master_Index.md")
