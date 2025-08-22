import os

# Generates a complete manifest of your repo (tracked files only)
os.system('git ls-files > repo_manifest.txt')

# For a broader manifest (all files, including untracked/ignored, but not .git internals)
os.system('find . -type f -not -path "*/.git/*" | sort > repo_manifest.txt')

# For manifest with file sizes
os.system('find . -type f -not -path "*/.git/*" -printf "%p\\t%s\\n" | sort > repo_manifest_sizes.txt')
