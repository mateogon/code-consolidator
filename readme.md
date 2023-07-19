# Repository Code Consolidator

This script consolidates all code from a repository into a single combined file, facilitating the reading of the repository by artificial intelligence language models.

## Usage

```bash
python consolidate.py <repo_dir>
```

This will generate a `combined_code.txt` file with all code concatenated.

## How it works

The main steps are:

### Parse .gitignore

Use `gitignore_parser` to get ignoring matching function.

```python
gitignore = os.path.join(repo_dir, '.gitignore')
matches = parse_gitignore(gitignore)
```

### Walk directory tree

Recursively walk repository directory using `os.walk()`.

```python
for root, dirs, files in os.walk(repo_dir):

  # Filter ignored files
  files = [f for f in files if not matches(os.path.join(root, f))]
```

### Copy Python code

For each `.py` file, read contents and append to output.

```python
for file in files:

  if file.endswith('.py'):

    with open(file) as f:
      code = f.read()
      combined_code += f"\n# {file_path}\n{code}\n"
```

### Write output file

Finally, write concatenated code string to `combined_code.txt`.

```python
with open('combined_code.txt', 'w') as f:
  f.write(combined_code)
```

## License

This code is released under the MIT License.

Let me know if you would like me to modify or expand the README content further.
