import os
import sys
from gitignore_parser import parse_gitignore

def copy_code(repo_dir):

  print(f"Copying code from {repo_dir}")

  # Parse .gitignore
  gitignore = os.path.join(repo_dir, '.gitignore')
  matches = parse_gitignore(gitignore)

  # Print directory tree
  combined_code = '\n# Directory structure:\n'

  for root, dirs, files in os.walk(repo_dir):

    # Filter files using matches function
    files = [f for f in files if not matches(os.path.join(root, f))]

    level = root.replace(repo_dir, '').count(os.sep) 
    indent = ' ' * 4 * (level)
    combined_code += '{}{}/\n'.format(indent, os.path.basename(root))

    subindent = ' ' * 4 * (level + 1)
    for f in files:
      combined_code += '{}{}\n'.format(subindent, f)

  # Copy non-ignored python code
  for root, dirs, files in os.walk(repo_dir):

    files = [f for f in files if not matches(os.path.join(root, f))]

    for file in files:
      if file.endswith('.py'):
        file_path = os.path.join(root, file)
        
        with open(file_path, 'r') as f:
          code = f.read()
          combined_code += f"\n#### file: {file_path}\n{code}\n"

  with open('combined_code.txt', 'w') as f:
    f.write(combined_code)  

if __name__ == '__main__':
  repo_dir = sys.argv[1]
  copy_code(repo_dir)