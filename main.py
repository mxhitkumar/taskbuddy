import os
import random
import subprocess
from datetime import datetime, timedelta

# --- Project Configuration (Extensible) ---
# Add new project types, file paths, and commit message templates here.
# {file} will be replaced with a randomly chosen filename.
PROJECT_TEMPLATES = {
    'react': {
        'files': [
            'src/App.js', 'src/index.js', 'src/components/Header.jsx', 
            'src/components/Footer.jsx', 'package.json', 'src/utils/api.js',
            'src/hooks/useUserData.js', 'public/index.html'
        ],
        'messages': [
            'feat(component): add new component logic to {file}',
            'fix(app): correct state management bug in {file}',
            'refactor(hooks): simplify hook in {file}',
            'style(css): adjust padding for {file}',
            'chore: update dependencies in {file}',
            'docs: update comments in {file}',
            'test: add unit test for {file}'
        ]
    },
    'django': {
        'files': [
            'apps/users/models.py', 'apps/api/views.py', 'project/urls.py', 
            'apps/core/forms.py', 'apps/users/admin.py', 'project/settings.py',
            'templates/base.html', 'static/css/style.css'
        ],
        'messages': [
            'feat(models): add {file} to new app',
            'fix(views): correct queryset in {file}',
            'refactor(urls): simplify routes in {file}',
            'style(template): format {file}',
            'chore: update settings in {file}',
            'test: add unit test for {file}',
            'docs(readme): update setup instructions'
        ]
    },
    'node': {
        'files': [
            'server.js', 'src/routes/api.js', 'src/controllers/authController.js', 
            'src/models/User.js', 'package.json', 'src/config/db.js',
            'src/middleware/auth.js', '.env.example'
        ],
        'messages': [
            'feat(api): add new endpoint to {file}',
            'fix(auth): resolve passport strategy bug in {file}',
            'refactor(server): optimize {file} imports',
            'chore: bump npm packages in {file}',
            'docs(readme): update setup instructions',
            'ci: update pipeline config',
            'fix(db): correct connection string in {file}'
        ]
    },
    'general': {
        'files': [
            'README.md', 'docs/guide.md', 'main.py', 'utils.py', 
            'config.ini', 'requirements.txt', '.gitignore'
        ],
        'messages': [
            'feat: add new feature logic to {file}',
            'fix: correct typo in {file}',
            'refactor: cleanup code in {file}',
            'docs: update {file}',
            'style: format {file} with black/prettier',
            'chore: general maintenance',
            'perf: optimize function in {file}'
        ]
    }
}

# --- Re-usable Core Function (Improved from original) ---

def make_commit(date, repo_path, filename, message):
    """
    Creates a single git commit at a specific date and time.
    
    Args:
        date (datetime): The datetime object for the commit.
        repo_path (str): The absolute path to the git repository.
        filename (str): The name of the file to modify.
        message (str): The commit message.

    Returns:
        tuple: (bool, str or None) indicating success and error message if any.
    """
    filepath = os.path.join(repo_path, filename)
    try:
        # Append a unique line to the file to ensure the commit is not empty
        # This will also create the file if it doesn't exist, but not the directory
        with open(filepath, "a") as f:
            f.write(f"Commit at {date.isoformat()}\n")
        
        # Git add
        subprocess.run(
            ["git", "add", filename], 
            cwd=repo_path, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        # Environment for setting commit date
        env = os.environ.copy()
        # Format: "YYYY-MM-DDTHH:MM:SS"
        date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str
        
        # Git commit
        subprocess.run(
            ["git", "commit", "-m", message], 
            cwd=repo_path, 
            env=env, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        return True, None # Success
    except (IOError, subprocess.CalledProcessError) as e:
        error_message = f"Error during commit for {date_str}:\n"
        if isinstance(e, subprocess.CalledProcessError):
            error_message += f"STDOUT: {e.stdout}\nSTDERR: {e.stderr}"
        else:
            error_message += str(e)
        return False, error_message # Failure
    except FileNotFoundError:
        return False, "Error: 'git' command not found. Is git installed and in your PATH?"

# --- Input Validation Helpers ---

def get_repo_path(prompt):
    """Gets a valid git repository path from the user."""
    while True:
        user_input = input(f"{prompt} (default: current directory): ").strip()
        path = user_input if user_input else "."
        
        git_dir = os.path.join(path, '.git')
        
        if os.path.isdir(git_dir):
            return os.path.abspath(path)
        elif os.path.isdir(path):
            print(f"Error: Path '{path}' is a directory, but not a git repository.")
            print("Please initialize it with 'git init' or provide a valid repo path.")
        else:
            print(f"Error: Path '{path}' does not exist or is not a directory.")

def get_project_config():
    """Asks user to select a project type."""
    print("\n(Q) What type of project are you working on?")
    print("  This helps generate realistic filenames and commit messages.")
    options = list(PROJECT_TEMPLATES.keys())
    
    for i, key in enumerate(options):
        print(f"  [{i+1}] {key.capitalize()}")
    
    while True:
        try:
            choice_str = input(f"  Choice (1-{len(options)}): ").strip()
            if not choice_str and 'general' in options:
                 print("  Selected: General (default)")
                 return PROJECT_TEMPLATES['general']
            
            choice = int(choice_str)
            if 1 <= choice <= len(options):
                project_key = options[choice-1]
                print(f"  Selected: {project_key.capitalize()}")
                return PROJECT_TEMPLATES[project_key]
            else:
                print(f"  Invalid choice. Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("  Invalid input. Please enter a number.")

def get_choice(prompt, choices):
    """Gets user input that must be one of the choices."""
    while True:
        user_input = input(f"{prompt} ({'/'.join(choices)}): ").strip().lower()
        if user_input in choices:
            return user_input
        else:
            print(f"Invalid choice. Please enter one of: {', '.join(choices)}")

def get_yes_no(prompt):
    """Gets a 'y' or 'n' answer."""
    return get_choice(prompt, ['y', 'n'])

def get_positive_int(prompt, min_val=1):
    """Gets an integer >= min_val."""
    while True:
        try:
            user_input = input(f"{prompt}: ").strip()
            value = int(user_input)
            if value >= min_val:
                return value
            else:
                print(f"Please enter a number that is at least {min_val}.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_date(prompt):
    """Gets a date in YYYY-MM-DD format."""
    while True:
        date_str = input(f"{prompt} (YYYY-MM-DD): ").strip()
        try:
            # Parse string to datetime object
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

# --- New CLI Flow Functions ---

def print_welcome():
    """Prints the welcome banner."""
    print("="*60)
    print("🌱 Welcome to graph-greener - GitHub Contribution Graph Commit Generator 🌱")
    print("="*60)
    print("This tool will help you create realistic commits in the past.\n")

def handle_single_day():
    """Handles the 'Single Day' commit logic and returns a list of datetimes."""
    print("\n--- Single Day Commit ---")
    
    # (Q1) Get date
    commit_date_start = get_date("(Q1) What date do you want to make commits on?")
    
    # (Q2) Get number of commits
    num_commits = get_positive_int("(Q2) How many commits do you want to make on this day?")
    
    # Generate commit list
    commits_to_make = []
    for i in range(num_commits):
        # Spread commits randomly throughout a "workday" (9am to 5pm)
        hour = random.randint(9, 16) # 9am to 4:59pm
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        commit_date = commit_date_start.replace(hour=hour, minute=minute, second=second)
        commits_to_make.append(commit_date)
        
    # Summary
    print("\n--- Summary ---")
    print(f"I will create {num_commits} commits on {commit_date_start.strftime('%Y-%m-%d')}.")
    print("Messages and filenames will be randomly generated based on your project type.")
        
    if get_yes_no("Is this correct? (y/n)") == 'y':
        return commits_to_make
    else:
        print("Operation cancelled.")
        return []

def handle_date_range():
    """Handles the 'Date Range' commit logic and returns a list of datetimes."""
    print("\n--- Date Range Commits ---")
    
    # (Q1) Start Date
    start_date = get_date("(Q1) What is the START date?")
    
    # (Q2) End Date
    while True:
        end_date = get_date("(Q2) What is the END date?")
        if end_date >= start_date:
            break
        print("End date must be on or after the start date.")
        
    # (Q3) Commit frequency mode
    print("\n(Q3) How do you want to set the number of commits?")
    print("  [1] Per Day: Set a fixed or random number of commits *per day*.")
    print("  [2] Total: Set a total number of commits to be spread *randomly* across the date range.")
    commit_mode = get_choice("  Choice", ['1', '2'])

    min_c = 0
    max_c = 0
    total_commits = 0
    
    if commit_mode == '1': # Per Day
        print("\n(Q3a) How many commits do you want to make per day?")
        print("  [1] A fixed number (e.g., exactly 5 commits every day).")
        print("  [2] A random range (e.g., between 1 and 5 commits per day).")
        commit_freq_choice = get_choice("  Choice", ['1', '2'])
        
        if commit_freq_choice == '1':
            num = get_positive_int("  How many commits per day?", min_val=1)
            min_c, max_c = num, num
        else:
            min_c = get_positive_int("  What is the MINIMUM commits per day?", min_val=0)
            while True:
                max_c = get_positive_int(f"  What is the MAXIMUM commits per day? (min {min_c})", min_val=min_c)
                break
    else: # Total
        total_commits = get_positive_int("\n(Q3a) How many TOTAL commits do you want to make in this range?", min_val=1)

    # (Q4) Weekends
    print("\n(Q4) How should commits be distributed across days?")
    print("  [1] Every Day (Mon - Sun): Commits spread evenly across all days.")
    print("  [2] Weekdays Only (Mon - Fri): No commits on Saturday or Sunday.")
    print("  [3] Mostly Weekdays (Natural): Commits are much more likely on weekdays, with a few on weekends.")
    day_selection = get_choice("  Choice", ['1', '2', '3'])
    
    # --- Summary ---
    print("\n--- Summary ---")
    print(f"I will create commits from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.")
    
    if commit_mode == '1':
        if min_c == max_c:
            print(f"Frequency: Exactly {min_c} commits per day.")
        else:
            print(f"Frequency: Between {min_c} and {max_c} commits per day.")
    else:
        print(f"Frequency: A total of {total_commits} commits will be spread across the range.")

    if day_selection == '1':
        print("Days: Every day (Mon - Sun).")
    elif day_selection == '2':
        print("Days: Weekdays only (Mon - Fri).")
    else:
        print("Days: Mostly weekdays (Natural style).")
        
    print("Messages and filenames will be randomly generated based on your project type.")

    if get_yes_no("Is this correct? (y/n)") != 'y':
        print("Operation cancelled.")
        return []

    # --- Generate Commit List ---
    commits_to_make = []
    
    if commit_mode == '1': # Per Day logic
        current_date = start_date
        delta = timedelta(days=1)
        
        while current_date <= end_date:
            is_weekend = current_date.weekday() >= 5 # 5 (Sat) or 6 (Sun)
            num_commits = 0
            
            if day_selection == '1': # Every day
                num_commits = random.randint(min_c, max_c)
            elif day_selection == '2': # Weekdays only
                if not is_weekend:
                    num_commits = random.randint(min_c, max_c)
            elif day_selection == '3': # Mostly Weekdays
                if not is_weekend:
                    # Full commits on weekdays
                    num_commits = random.randint(min_c, max_c)
                else:
                    # 25% chance of committing on a weekend
                    if random.random() < 0.25 and max_c > 0: 
                        # If so, commit 1 or 2, but never more than the daily max
                        num_commits = min(random.randint(1, 2), max_c)
            
            for i in range(num_commits):
                hour = random.randint(9, 16)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                commit_date = current_date.replace(hour=hour, minute=minute, second=second)
                commits_to_make.append(commit_date)
                
            current_date += delta
            
    else: # Total commits logic
        # 1. Build weighted list of available dates
        weighted_dates = []
        current_date = start_date
        delta = timedelta(days=1)
        
        weekday_weight = 10 # 10 "chances" for a weekday
        weekend_weight = 2  # 2 "chances" for a weekend day (if 'mostly_weekdays')
        
        while current_date <= end_date:
            is_weekend = current_date.weekday() >= 5
            
            if day_selection == '1': # Every day
                weighted_dates.append(current_date)
            elif day_selection == '2': # Weekdays only
                if not is_weekend:
                    weighted_dates.append(current_date)
            elif day_selection == '3': # Mostly Weekdays
                if not is_weekend:
                    weighted_dates.extend([current_date] * weekday_weight)
                else:
                    weighted_dates.extend([current_date] * weekend_weight)
            
            current_date += delta
            
        if not weighted_dates:
            print("No available days in the selected range with the chosen settings. No commits created.")
            return []
            
        # 2. Randomly pick dates from the weighted list for the total number of commits
        for i in range(total_commits):
            picked_date = random.choice(weighted_dates)
            
            hour = random.randint(9, 16)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            commit_date = picked_date.replace(hour=hour, minute=minute, second=second)
            commits_to_make.append(commit_date)

    return commits_to_make

def process_commits(dates_to_commit, repo_path, project_config):
    """
    Iterates over the list of dates, generates a realistic commit,
    and creates it.
    """
    files_list = project_config['files']
    message_templates = project_config['messages']
    
    total_commits = len(dates_to_commit)
    if total_commits == 0:
        print("No commits to make.")
        return

    print(f"\nProcessing {total_commits} commits...")
    
    # Sort commits by date to ensure they are made in chronological order
    dates_to_commit.sort()
    
    success_count = 0
    fail_count = 0
    
    for i, commit_date in enumerate(dates_to_commit):
        # 1. Generate commit details
        filename = random.choice(files_list)
        message_template = random.choice(message_templates)
        message = message_template.replace('{file}', filename)
        
        filepath = os.path.join(repo_path, filename)
        
        # 2. Ensure file and directory exist
        try:
            # Create directory if it doesn't exist (e.g., for 'src/components/Header.jsx')
            dir_name = os.path.dirname(filepath)
            if dir_name: # Only run if there is a directory path
                os.makedirs(dir_name, exist_ok=True)
                
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(f"# Initial content for {filename}\n")
                # We MUST 'git add' this NEW file before make_commit can commit it
                subprocess.run(
                    ["git", "add", filepath], 
                    cwd=repo_path, 
                    check=True, 
                    capture_output=True, 
                    text=True
                )
        except (IOError, subprocess.CalledProcessError) as e:
            print(f"  ^ FAILED: Could not create/add new file {filepath}: {e}")
            fail_count += 1
            break
        except FileNotFoundError:
             print(f"\nError: 'git' command not found. Is git installed and in your PATH?")
             fail_count += 1
             break

        # 3. Make the commit
        print(f"[{i+1}/{total_commits}] Committing to '{filename}' at {commit_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Message: {message}")
        
        success, error_msg = make_commit(commit_date, repo_path, filename, message)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
            print(f"  ^ FAILED: {error_msg}")
            print("  Stopping operation to prevent further errors.")
            break # Stop on first failure
            
    print("\n--- Processing Complete ---")
    print(f"Successfully created: {success_count} commits.")
    if fail_count > 0:
        print(f"Failed: {fail_count} commits.")
        print("Operation was stopped. Please check the error message above.")
        print("Your local repository might be in a strange state. No changes were pushed.")
    else:
        print("All local commits successful.")
        print("\nPushing commits to your remote repository...")
        try:
            # A simple push. If it fails, the user needs to resolve it.
            subprocess.run(
                ["git", "push"], 
                cwd=repo_path, 
                check=True, 
                capture_output=True, 
                text=True
            )
            print("\n✅ All done! Check your GitHub contribution graph in a few minutes.")
            print("Tip: Use a dedicated repository for best results. Happy coding!")
        except subprocess.CalledProcessError as e:
            print("\n--- Push FAILED ---")
            print("STDERR:", e.stderr)
            print("STDOUT:", e.stdout)
            print("\nYour local commits were created, but the push to remote failed.")
            print("This is often because the remote has changes you don't have locally.")
            print("Try running 'git pull' in your repo, or if this is a dedicated repo,")
            print("you can try 'git push --force' (DANGEROUS: overwrites remote history).")
        except FileNotFoundError:
             print(f"\nError: 'git' command not found. Is git installed and in your PATH?")


def main():
    """Main function to run the CLI."""
    print_welcome()
    
    try:
        # Get repo and project info once
        repo_path = get_repo_path("Enter the path to your local git repository")
        project_config = get_project_config()
        
        # Main menu loop
        while True:
            print("\n--- Main Menu ---")
            print("What do you want to do?")
            print("  [1] Single Day: Add one or more commits to a single, specific date.")
            print("  [2] Date Range: Fill in commits over a period of time.")
            print("  [q] Quit: Exit the program.")
            
            choice = get_choice("Please enter your choice", ['1', '2', 'q'])
            
            commits_to_make = []
            
            if choice == '1':
                commits_to_make = handle_single_day()
            elif choice == '2':
                commits_to_make = handle_date_range()
            elif choice == 'q':
                print("Goodbye!")
                break
                
            if commits_to_make:
                process_commits(commits_to_make, repo_path, project_config)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Goodbye!")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

