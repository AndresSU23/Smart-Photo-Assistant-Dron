#!/usr/bin/env python3
import csv
import sys
import subprocess
import os
import json
import time

def get_existing_issues():
    """Fetches list of existing issue titles to avoid duplicates."""
    print("Fetching existing issues to avoid duplicates...")
    try:
        # Get all issues (open and closed)
        result = subprocess.run(
            ['gh', 'issue', 'list', '--state', 'all', '--limit', '1000', '--json', 'title'],
            capture_output=True, text=True, check=True
        )
        issues = json.loads(result.stdout)
        return {issue['title'] for issue in issues}
    except Exception as e:
        print(f"Warning: Could not fetch existing issues: {e}")
        return set()

def create_label_if_missing(label_name):
    """Attempts to create a label. Ignores errors if it already exists."""
    # fast check: try to create it. If it fails, it likely exists.
    subprocess.run(
        ['gh', 'label', 'create', label_name, '--color', 'ededed', '--description', 'Imported via script'],
        capture_output=True, text=True 
        # We don't check=True because we expect this to fail if label exists
    )

def create_issues(csv_file):
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)

    existing_titles = get_existing_issues()

    print(f"Reading issues from {csv_file}...")

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            title = row.get('title', '').strip()
            body_text = row.get('body', '').strip().replace(r'\n', '\n')
            labels_raw = row.get('labels', '').strip()
            milestone = row.get('milestone', '').strip()

            if not title:
                continue

            # Skip if issue already exists
            if title in existing_titles:
                print(f"Skipping (already exists): {title}")
                continue

            print(f"Processing: {title}")

            # 1. Handle Labels (Create them if they don't exist)
            label_args = []
            if labels_raw:
                label_list = labels_raw.split(';')
                for label in label_list:
                    clean_label = label.strip()
                    if clean_label:
                        create_label_if_missing(clean_label)
                        label_args.extend(['--label', clean_label])

            # 2. Construct the Command
            # We use --body-file - to read from stdin, avoiding quote parsing errors
            cmd = [
                'gh', 'issue', 'create',
                '--title', title,
                '--body-file', '-', 
                '--milestone', milestone
            ] + label_args

            # 3. Execute
            try:
                process = subprocess.Popen(
                    cmd, 
                    stdin=subprocess.PIPE, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                # Pass the body text safely through stdin
                stdout, stderr = process.communicate(input=body_text)

                if process.returncode != 0:
                    print(f"Failed to create '{title}'")
                    print(f"Error: {stderr}")
                else:
                    print(f"Success: {stdout.strip()}")
                    # Small sleep to prevent hitting GitHub API rate limits too hard
                    time.sleep(1)

            except Exception as e:
                print(f"CRITICAL ERROR on '{title}': {e}")

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'issues.csv'
    create_issues(filename)
