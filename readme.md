# Repository Code Consolidator

This script consolidates all code from a repository into a single combined file, facilitating the reading of the repository by artificial intelligence language models.

## Installation

```bash
pip install gitignore_parser
```

## Usage

```bash
python consolidate.py <repo_dir>
```

This will generate a `combined_code.txt` file with all code concatenated.

## How it works

The main steps involved in the script are as follows:

### Parse .gitignore

The script checks if a `.gitignore` file exists in the repository directory. If found, it uses the `gitignore_parser` library to parse the `.gitignore` file and obtain the ignoring matching function.

```python
gitignore = os.path.join(repo_dir, '.gitignore')
if os.path.exists(gitignore):
    matches = parse_gitignore(gitignore)
else:
    print('.gitignore not found, skipping ignore checks')
    matches = None
```

### Walk directory tree

The script recursively walks through the repository directory using `os.walk()` to traverse all subdirectories and files. It filters out the ignored files based on the matching function obtained from the `.gitignore` file.

```python
for root, dirs, files in os.walk(repo_dir):
    # Filter ignored files
    files = [f for f in files if not matches(os.path.join(root, f))]
```

### Copy Python code

For each file, the script checks if it is a Python file (ends with `.py`). If it is, the script reads the contents of the file and appends it to the output string.

```python
for file in files:
    if file.endswith('.py'):
        file_path = os.path.join(root, file)
        with open(file_path, 'r') as f:
            code = f.read()
            combined_code += f"\n#### file: {file_path}\n{code}\n"
```

### Write output file

Finally, the script writes the concatenated code string to the `combined_code.txt` file.

```python
output_file = 'combined_code.txt'

with open(output_file, 'w') as f:
    f.write(combined_code)
```

## License

This code is released under the MIT License.

I apologize for the confusion earlier, and thank you for bringing it to my attention. The updated README now accurately reflects the steps performed by the code.
