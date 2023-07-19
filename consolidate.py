import os
import sys
from gitignore_parser import parse_gitignore
import argparse

def copy_code(repo_dir):
    print(f"Copying code from {repo_dir}")

    # Parse .gitignore
    gitignore = os.path.join(repo_dir, '.gitignore')
    if os.path.exists(gitignore):
        matches = parse_gitignore(gitignore)
    else:
        print('.gitignore not found, skipping ignore checks')
        matches = None

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

    return combined_code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Consolidate repository code into a text file.')
    parser.add_argument('repo_dir', help='Path to the repository directory')
    args = parser.parse_args()

    repo_dir = args.repo_dir
    if not os.path.isdir(repo_dir):
        sys.exit("Error: The specified repository directory does not exist.")

    try:
        combined_code = copy_code(repo_dir)
        output_file = 'combined_code.txt'

        with open(output_file, 'w') as f:
            f.write(combined_code)

        print(f"Code copied and saved to {output_file} successfully.")
    except Exception as e:
        sys.exit(f"An error occurred while copying the code: {str(e)}")
