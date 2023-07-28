import os
import sys
import argparse
from gitignore_parser import parse_gitignore
from pathlib import Path

# Function to parse the .gitignore file of the repository.
def parse_ignore_file(repo_path):
    gitignore_path = repo_path / '.gitignore'
    # If .gitignore file exists, parse it to create a matcher function, else return a function that always returns False.
    return parse_gitignore(gitignore_path) if gitignore_path.exists() else (lambda s: False)

# Function to filter out the files that should not be included in the final output.
def filter_files(files, matcher):
    return [f for f in files if not matcher(str(f)) and '.git' not in str(f)]

# Function to filter out the directories that should not be included in the final output.
def filter_dirs(dirs, matcher, root):
    return [d for d in dirs if not matcher(os.path.join(root, d)) and '.git' not in d]

# Function to print and collect the files of a directory tree.
def print_and_collect_files(repo_path, matcher):
    return _walk_files(repo_path, matcher, lambda f, dir: f"{' ' * 4 * (len(f.parts) - len(repo_path.parts))}{f.name}\n", dir=True)

# Function to copy the content of the files from the repository.
def copy_files(repo_path, matcher):
    return _walk_files(repo_path, matcher, lambda f, dir: f"\n#### file: {f}\n{f.read_text(errors='replace')}\n" if not dir else "")

# Helper function to walk the files of the repository and process them.
def _walk_files(repo_path, matcher, file_processor, dir=False):
    combined_files = ""

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = filter_dirs(dirs, matcher, root)
        files = filter_files((Path(root) / f for f in files), matcher)

        if dir:
            combined_files += file_processor(Path(root), True)
        for f in files:
            combined_files += file_processor(f, False)

    return combined_files

# Function to consolidate the code from the repository.
def consolidate_code(repo_path, mode):
    matcher = parse_ignore_file(repo_path)
    combined_files = ""

    if mode in ['tree', 'both']:
        combined_files += print_and_collect_files(repo_path, matcher)
    if mode in ['code', 'both']:
        combined_files += copy_files(repo_path, matcher)

    return combined_files

# Main function that parses the arguments and controls the flow of the script.
def main():
    parser = argparse.ArgumentParser(description='Consolidate repository files into a text file.')
    parser.add_argument('repo_dir', help='Path to the repository directory')
    parser.add_argument('mode', help='Consolidation mode: tree, code or both')
    args = parser.parse_args()

    repo_path = Path(args.repo_dir)
    if not repo_path.is_dir():
        sys.exit("Error: The specified repository directory does not exist.")

    try:
        combined_files = consolidate_code(repo_path, args.mode)
        output_file = 'combined_files.txt'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined_files)

        print(f"Files copied and saved to {output_file} successfully.")
    except Exception as e:
        sys.exit(f"An error occurred while copying the files: {str(e)}")

# Entry point of the script.
if __name__ == '__main__':
    main()
