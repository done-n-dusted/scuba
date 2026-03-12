import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e.stderr}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 make_commit.py '<commit message>'")
        sys.exit(1)

    message = sys.argv[1]
    
    # Ensure no trailing newline or extra whitespace
    message = message.strip()
    
    # 1. Stage all changes (including untracked)
    print("Staging changes...")
    run_command(['git', 'add', '.'])
    
    # 2. Check if there's anything to commit
    status = run_command(['git', 'status', '--porcelain'])
    if not status:
        print("Nothing to commit.")
        sys.exit(0)
    
    # 3. Commit
    print(f"Committing with message: {message}")
    # Using -m with a single string to ensure no extra headers/footers
    result = run_command(['git', 'commit', '-m', message])
    if result:
        print("Commit successful!")
        print(result)

if __name__ == "__main__":
    main()
