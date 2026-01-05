#!/usr/bin/env python3
import csv
import sys
import subprocess
import os

def create_issues(csv_file):
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)

    print(f"Reading issues from {csv_file}...")

    with open(csv_file, 'r', encoding='utf-8') as f:
        # csv.DictReader automatically handles quotes and commas inside quotes
        reader = csv.DictReader(f)
        
        for row in reader:
            title = row.get('title', '').strip()
            body = row.get('body', '').strip()
            labels_raw = row.get('labels', '').strip()
            milestone = row.get('milestone', '').strip()

            if not title:
                continue

            print(f"Creating issue: {title}")

            # Construct the GitHub CLI command
            cmd = [
                'gh', 'issue', 'create',
                '--title', title,
                '--body', body.replace(r'\n', '\n'), # Handle escaped newlines if present
                '--milestone', milestone
            ]

            # Handle semicolon-separated labels (e.g., "setup;ros2")
            if labels_raw:
                label_list = labels_raw.split(';')
                for label in label_list:
                    if label.strip():
                        cmd.extend(['--label', label.strip()])

            # Execute the command
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to create issue '{title}'. Exit code: {e.returncode}")
                # Optional: exit(1) if you want the pipeline to fail immediately
                # sys.exit(1) 

if __name__ == "__main__":
    # Get filename from args or default to issues.csv
    filename = sys.argv[1] if len(sys.argv) > 1 else 'issues.csv'
    create_issues(filename)
