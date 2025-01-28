import os
import sys
import argparse
from gitignore_parser import parse_gitignore
from pathlib import Path

# Lista de archivos a ignorar
IGNORE_FILES = ['package-lock.json']

def parse_ignore_file(repo_path):
    gitignore_path = repo_path / '.gitignore'
    return parse_gitignore(gitignore_path) if gitignore_path.exists() else (lambda s: False)
def is_image(file_path):
    """
    Determines if a file is an image based on its extension.
    """
    image_extensions = [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', 
        '.tiff', '.svg', '.webp'  # Added .webp here
    ]
    return any(file_path.lower().endswith(ext) for ext in image_extensions)

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

def filter_files(files, matcher, file_set=None):
    filtered_files = []
    for f in files:
        file_resolved = f.resolve()
        file_path = str(f).replace("\\", "/")  # Normalize path
        if not matcher(file_path) and '.git' not in file_path and f.name not in IGNORE_FILES:
            if file_set is None or file_resolved in file_set:
                print(f"Incluyendo: {file_resolved}")
                filtered_files.append(f)
            else:
                print(f"Excluyendo: {file_resolved}")
    return filtered_files


def filter_files_for_code(files, matcher, file_set=None):
    filtered_files = []
    for f in files:
        file_resolved = f.resolve()
        if not matcher(str(f)) and '.git' not in str(f) and not is_image(str(f)) and not ignore(str(f)) and f.name not in IGNORE_FILES:
            if file_set is None or file_resolved in file_set:
                #print(f"Incluyendo: {file_resolved}")
                filtered_files.append(f)
            else:
                print(f"Excluyendo: {file_resolved}")
    return filtered_files

def print_and_collect_files(repo_path, matcher, file_set=None):
    return _walk_files(repo_path, matcher, lambda f, dir: f"{str(f)}\n", dir=True, file_set=file_set)

def copy_files(repo_path, matcher, file_set=None):
    return _walk_files(repo_path, matcher, lambda f, dir: f"\n#### file: {f}\n{f.read_text(errors='replace')}\n" if not dir else "", file_set=file_set, code=True)

def _walk_files(repo_path, matcher, file_processor, dir=False, file_set=None, code=False):
    combined_files = ""

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = filter_dirs(dirs, matcher, root)
        path_objs = (Path(root) / f for f in files)
        if code:
            filtered_files = filter_files_for_code(path_objs, matcher, file_set=file_set)
        else:
            filtered_files = filter_files(path_objs, matcher, file_set=file_set)

        # Filtrar el directorio actual si no tiene archivos incluidos
        if dir and file_set:
            dir_path = Path(root).resolve()
            is_dir_included = any(f.resolve().is_relative_to(dir_path) for f in file_set)
            if not is_dir_included:
                continue  # Saltar directorio si no tiene archivos incluidos

        if dir:
            combined_files += file_processor(Path(root), True)
        for f in filtered_files:
            combined_files += file_processor(f, False)

    return combined_files

def read_file_list(file_list_path, repo_path):
    with open(file_list_path, 'r') as file:
        return set((repo_path / line.strip()).resolve() for line in file if line.strip())

def consolidate_code(repo_path, mode, file_set=None):
    matcher = parse_ignore_file(repo_path)
    combined_files = ""

    if mode in ['tree', 'both']:
        combined_files += print_and_collect_files(repo_path, matcher, file_set=file_set)
    if mode in ['code', 'both']:
        combined_files += copy_files(repo_path, matcher, file_set=file_set)

    return combined_files

def main():
    parser = argparse.ArgumentParser(description='Consolidate repository files into a text file.')
    parser.add_argument('repo_dir', help='Path to the repository directory')
    parser.add_argument('mode', choices=['tree', 'code', 'both'], help='Consolidation mode: tree, code or both')
    parser.add_argument('--file_list', help='Path to a text file containing the list of files to copy')
    args = parser.parse_args()

    repo_path = Path(args.repo_dir).resolve()
    if not repo_path.is_dir():
        sys.exit("Error: The specified repository directory does not exist.")

    try:
        file_set = read_file_list(args.file_list, repo_path) if args.file_list else None

        combined_files = consolidate_code(repo_path, args.mode, file_set=file_set)
        output_file = 'combined_files.txt'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined_files)

        print(f"Files copied and saved to {output_file} successfully.")
    except Exception as e:
        sys.exit(f"An error occurred while copying the files: {str(e)}")

if __name__ == '__main__':
    main()
