# Repository Code Consolidator

This Python script provides a unified way to gather all the code from a repository into a singular text file. This feature aims to provide an easy, digestible format for artificial intelligence language models to analyze repository content.

## Getting Started

### Dependencies

To run this script, you'll need to install the `gitignore_parser` library. You can do this using the following command:

```bash
pip install gitignore_parser
```

### Usage

Here's how you use this script:

```bash
python consolidate.py <repo_dir> <mode>
```

This command will create a text file named `combined_files.txt` that contains the repository's code content based on the specified mode ('tree', 'code', or 'both').

## How It Works

### Ignoring Unwanted Files

The script first verifies the presence of a `.gitignore` file within the repository. If such a file exists, the script employs the `gitignore_parser` library to derive a function that matches the ignore rules defined in the `.gitignore` file.

```python
matcher = parse_ignore_file(repo_path)
```

If no `.gitignore` file exists, or if a file is not listed within it, the script will proceed to include that file's content in its operations. The `.git` directory, if present, is always ignored.

### Walking Through Repository

The script employs `os.walk()` to traverse the directory tree of the repository, covering all directories and files recursively. During this walk, the script filters out any ignored files and directories based on the derived matching function from the `.gitignore` file.

```python
for root, dirs, files in os.walk(repo_path):
    dirs[:] = filter_dirs(dirs, matcher, root)
    files = filter_files((Path(root) / f for f in files), matcher)
```

### Processing Repository Content

Depending on the specified mode, the script either:

- Prints and collects the names of the files (in 'tree' mode),
- Copies the content of the files (in 'code' mode),
- Or does both (in 'both' mode).

```python
combined_files = consolidate_code(repo_path, args.mode)
```

### Saving Output

The script consolidates all the processed content into a single string and writes it into a file named `combined_files.txt`.

```python
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(combined_files)
```

## License

This project is licensed under the MIT License.
