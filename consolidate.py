import os
import sys
import argparse
from gitignore_parser import parse_gitignore
from pathlib import Path

# Function to parse the .gitignore file of the repository.
def parse_ignore_file(repo_path):
    gitignore_path = repo_path / '.gitignore'
    return parse_gitignore(gitignore_path) if gitignore_path.exists() else (lambda s: False)

# Helper function to determine if a file or directory should be skipped
def is_skippable_file(filename):
    # Define a set of skippable file patterns or exact names
    skippable_files = {
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',  # image files
        '.pyc', '.pyo',  # Python cache files
        '.db', '.sqlite', '.sqlite3',  # Database files
        'package-lock.json'  # auto-generated large files
    }
    # Check if the file name exactly matches any skippable files
    if filename in skippable_files:
        return True
    # Check if the file ends with any skippable extensions or directory names
    return any(filename.endswith(ext) for ext in skippable_files if ext.startswith('.'))

def filter_files(files, matcher, file_list=None):
    # Update this to include skippable file check
    return [f for f in files if not matcher(str(f))
            and '.git' not in str(f)
            and not is_skippable_file(f.name)
            and (file_list is None or str(f) in file_list)]

def filter_dirs(dirs, matcher, root):
    # Exclude __pycache__ directories directly
    return [d for d in dirs if not matcher(os.path.join(root, d))
            and '.git' not in d
            and d != '__pycache__']

def print_and_collect_files(repo_path, matcher):
    return _walk_files(repo_path, matcher, lambda f, dir: f"{' ' * 4 * (len(f.parts) - len(repo_path.parts))}{f.name}\n", dir=True)

def copy_files(repo_path, matcher, file_list=None):
    return _walk_files(repo_path, matcher, lambda f, dir: f"\n#### file: {f}\n{f.read_text(errors='replace')}\n" if not dir else "", file_list=file_list)

def _walk_files(repo_path, matcher, file_processor, dir=False, file_list=None):
    combined_files = ""

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = filter_dirs(dirs, matcher, root)
        files = filter_files((Path(root) / f for f in files), matcher, file_list=file_list)

        if dir:
            combined_files += file_processor(Path(root), True)
        for f in files:
            combined_files += file_processor(f, False)

    return combined_files

def read_file_list(file_list_path):
    with open(file_list_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def consolidate_code(repo_path, mode, file_list_path=None):
    matcher = parse_ignore_file(repo_path)
    combined_files = ""
    file_list = read_file_list(file_list_path) if file_list_path else None

    if mode in ['tree', 'both']:
        combined_files += print_and_collect_files(repo_path, matcher)
    if mode in ['code', 'both']:
        combined_files += copy_files(repo_path, matcher, file_list=file_list)

    return combined_files

def main():
    parser = argparse.ArgumentParser(description='Consolidate repository files into a text file.')
    parser.add_argument('repo_dir', help='Path to the repository directory')
    parser.add_argument('mode', help='Consolidation mode: tree, code or both')
    parser.add_argument('--file_list', help='Path to a text file containing the list of files to copy')
    args = parser.parse_args()

    repo_path = Path(args.repo_dir)
    if not repo_path.is_dir():
        sys.exit("Error: The specified repository directory does not exist.")

    try:
        combined_files = consolidate_code(repo_path, args.mode, file_list_path=args.file_list)
        output_file = 'combined_files.txt'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined_files)

        print(f"Files copied and saved to {output_file} successfully.")
    except Exception as e:
        sys.exit(f"An error occurred while copying the files: {str(e)}")

if __name__ == '__main__':
    main()
