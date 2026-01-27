import os
import tarfile
import re
import shutil
from collections import defaultdict

def archive_processed_files():
    processed_dir = "processed"
    archive_dir = os.path.join(processed_dir, "archive")
    
    # regex to match medium-YYYY-MM-DD.sql
    file_pattern = re.compile(r"medium-(\d{4}-\d{2})-\d{2}\.sql$")
    
    if not os.path.exists(processed_dir):
        print(f"Directory {processed_dir} not found.")
        return

    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"Created archive directory: {archive_dir}")

    # Group files by YYYY-MM
    monthly_groups = defaultdict(list)
    files = [f for f in os.listdir(processed_dir) if os.path.isfile(os.path.join(processed_dir, f))]
    
    for filename in files:
        match = file_pattern.match(filename)
        if match:
            month_key = match.group(1) # YYYY-MM
            monthly_groups[month_key].append(filename)

    if not monthly_groups:
        print("No files to archive.")
        return

    for month, file_list in monthly_groups.items():
        archive_name = f"medium-{month}.tar.gz"
        archive_path = os.path.join(archive_dir, archive_name)
        
        print(f"Archiving {len(file_list)} files for {month} into {archive_name}...")
        
        try:
            with tarfile.open(archive_path, "w:gz") as tar:
                for filename in file_list:
                    file_path = os.path.join(processed_dir, filename)
                    tar.add(file_path, arcname=filename)
            
            print(f"Successfully created {archive_name}. Deleting original files...")
            
            for filename in file_list:
                os.remove(os.path.join(processed_dir, filename))
                
        except Exception as e:
            print(f"Error archiving {month}: {e}")

if __name__ == "__main__":
    # Change CWD to the project root if the script is run from 'scripts'
    if os.path.basename(os.getcwd()) == "scripts":
        os.chdir("..")
    
    archive_processed_files()
