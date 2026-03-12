import subprocess
import sys
import os

def get_git_diff_stat():
    try:
        # Get the files that are staged
        result = subprocess.run(['git', 'diff', '--cached', '--stat'], 
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def get_git_diff_summary():
    try:
        # Get a more detailed diff summary if needed
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        return []

def main():
    diff_stat = get_git_diff_stat()
    if not diff_stat:
        print("No staged changes found. Use 'git add' first.")
        sys.exit(1)

    files = get_git_diff_summary()
    
    # Simple logic to suggest a commit message based on file changes
    if not files or files == ['']:
        print("No changes found.")
        sys.exit(0)

    # Example: If main.py is in the list, suggest "Add main.py"
    # For now, let's just show the stat and ask the user for a message,
    # or let the AI (me) use this info.
    
    print("Files staged for commit:")
    print(diff_stat)
    
    # We can't really "suggest" a perfect message without LLM context,
    # but the AI using this script will see the files.
    # The crucial part is to avoid any extra footer.

if __name__ == "__main__":
    main()
