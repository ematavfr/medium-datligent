import sys
import datetime
import subprocess
import time
import os

def main():
    if len(sys.argv) != 3:
        print("Usage: python batch_ingest.py YYYY-MM-DD YYYY-MM-DD")
        print("Example: python batch_ingest.py 2025-11-11 2025-11-22")
        sys.exit(1)

    start_date_str = sys.argv[1]
    end_date_str = sys.argv[2]

    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        sys.exit(1)

    if start_date > end_date:
        print("Start date must be before or equal to end date.")
        sys.exit(1)

    current_date = start_date
    
    # Path to ingest_medium.py - assuming we run this from project root or scripts dir
    # Let's assume we run from project root for now, or handle relative paths
    script_path = os.path.join("ingestion", "ingest_medium.py")
    if not os.path.exists(script_path):
        # Try running from scripts dir context
        script_path = os.path.join("..", "ingestion", "ingest_medium.py")
        if not os.path.exists(script_path):
             print("Could not find ingest_medium.py")
             sys.exit(1)

    print(f"Starting batch ingestion from {start_date} to {end_date}...")

    # We will run the command from the 'ingestion' directory so that relative paths in ingest_medium.py work as expected
    ingestion_dir = os.path.join(os.getcwd(), "ingestion")
    
    if not os.path.exists(ingestion_dir):
        print(f"Could not find ingestion directory at {ingestion_dir}")
        sys.exit(1)

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\n--- Processing {date_str} ---")
        
        # Executable and script relative to ingestion_dir
        python_executable = "venv/bin/python"
        script_name = "ingest_medium.py"

        cmd = [python_executable, script_name, date_str]
        
        try:
            # Run from ingestion dir
            result = subprocess.run(cmd, cwd=ingestion_dir, capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                print(f"Error processing {date_str}:")
                print(result.stderr)
            else:
                print(f"Successfully processed {date_str}")
        except Exception as e:
            print(f"Failed to execute script for {date_str}: {e}")

        current_date += datetime.timedelta(days=1)
        
        if current_date <= end_date:
            print("Waiting 10 seconds before next day to avoid rate limits...")
            time.sleep(10)

    print("\nBatch ingestion completed.")

if __name__ == "__main__":
    main()
