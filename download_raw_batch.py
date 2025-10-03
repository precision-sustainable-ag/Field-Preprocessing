import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

from tqdm import tqdm

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

parser = argparse.ArgumentParser(description="Process batches with RawTherapee")
parser.add_argument("batch_names", nargs='+', help="One or more batch names to process")
parser.add_argument("--username", required=True, help="Username for remote server in sunny")
args = parser.parse_args()

batch_names = args.batch_names   # This is now a list of one or more batch names
username = args.username

def download_from_azure(batch_name):
    export_dir = "/home/psa_images/temp_data/field_data/"# + str(batch_name)
    os.makedirs(export_dir, exist_ok=True)
    exe_command = f"/home/psa_images/field_tools/azcopy copy \
        'SAS_key_here' \
        {export_dir} \
        --recursive \
        --overwrite=false"
        
    print(exe_command)
    try:
        # Run the rawtherapee command
        process_id = subprocess.run(exe_command, shell=True, check=True)
    except Exception as e:
        raise e
    print("Raw data has been downloaded for batch " + str(batch_name))
    subprocess.call(['chmod', '-R', '777', export_dir + str(batch_name)])


def find_unprocessed_files(batch_name: str, username: str) -> List[Path]:
    """Find RAW files in the remote batch directory that do not have corresponding developed JPGs."""
    print(f"Finding unprocessed files for batch {batch_name} on remote server...")
    # Define remote directories
    raw_dir = f"/mnt/research-projects/r/raatwell/longterm_images3/field-batches/{batch_name}/raws"
    dev_dir = f"/mnt/research-projects/r/raatwell/longterm_images3/field-batches/{batch_name}/developed-images"

    # List RAW files remotely
    raw_cmd = [
        "ssh", f"{username}@sunny.ece.ncsu.edu",
        f"find {raw_dir} -type f -name '*.ARW'"
    ]
    raw_files = subprocess.check_output(raw_cmd).decode().splitlines()

    # List developed JPGs remotely
    dev_cmd = [
        "ssh", f"{username}@sunny.ece.ncsu.edu",
        f"find {dev_dir} -type f -name '*.jpg'"
    ]
    dev_files = subprocess.check_output(dev_cmd).decode().splitlines()

    # Compare stems
    dev_stems = {Path(f).stem for f in dev_files}
    unprocessed_files = [f for f in raw_files if Path(f).stem not in dev_stems]

    print(f"Found {len(unprocessed_files)} unprocessed files out of {len(raw_files)} total raws.")
    return unprocessed_files

def download_from_nfs(batch_name: str, username: str):
    # Path where batch is stored in the NFS-mounted directory
    unprocessed_files = find_unprocessed_files(batch_name, username)
    if not unprocessed_files:
        print(f"No unprocessed files found for batch {batch_name}. Exiting.")
        return
    
    # Local path to copy data to
    export_dir = Path(f"temp_data/{batch_name}/raws")
    export_dir.mkdir(parents=True, exist_ok=True)

    for src_file in tqdm(unprocessed_files, desc="Copying files"):
        dest_file = export_dir / Path(src_file).parent.name / Path(src_file).name
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        subprocess.call([
            "rsync", "-avz",
            f"{username}@sunny.ece.ncsu.edu:{src_file}",
            str(dest_file)
        ])
        print(f"Copied {src_file} -> {dest_file}")

    subprocess.call(['chmod', '-R', '777', str(export_dir)])
    print(f"Raw data has been downloaded for batch {batch_name}")

if __name__ == "__main__":
    for batch_name in tqdm(batch_names, desc="Processing batches"):
        download_from_nfs(batch_name, username)