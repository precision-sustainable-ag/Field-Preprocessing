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
parser.add_argument("batch_name", help="Name of the batch to process")
parser.add_argument("--username", help="Username for remote server in sunny")
args = parser.parse_args()

batch_name = args.batch_name
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
    # Mount the remote directory 
    remote_path = f"{username}@sunny.ece.ncsu.edu:/mnt/research-projects/r/raatwell/longterm_images3/field-batches/{batch_name}"
    local_path = Path("/tmp") / batch_name
    local_path.mkdir(parents=True, exist_ok=True)

    print(f"syncing {remote_path} to {local_path}")
    subprocess.call([
        "rsync",
        "-avz",
        "--progress",
        remote_path,
        str(local_path)
    ])

    raw_dir = local_path / "raws"
    raw_imgs = list(raw_dir.rglob("*.ARW"))

    batch_developed = local_path / "developed-images"
    developed_imgs = sorted(batch_developed.glob("*.jpg"))
    developed_img_stems = {img.stem for img in developed_imgs}

    unprocessed_files = [img for img in raw_imgs if img.stem not in developed_img_stems]
    return unprocessed_files

def download_from_nfs(batch_name: str, username: str):
    # Path where batch is stored in the NFS-mounted directory
    unprocessed_files = find_unprocessed_files(batch_name, username)

    if not unprocessed_files:
        print(f"No unprocessed files found for batch {batch_name}. Exiting.")
        return
    
    # Local path to copy data to
    export_dir = Path("temp_data/field_data", batch_name)
    export_dir.mkdir(parents=True, exist_ok=True)

    # Copy unprocessed files to local directory
    for src_file in tqdm(unprocessed_files, desc="Copying files"):
        relative_path = src_file.relative_to(Path("/tmp") / batch_name)  # preserves relative path within batch/raws/
        dest_file = export_dir / relative_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src_file, dest_file)
        print(f"Copied {src_file} to {dest_file}")
    # Set permissions if needed
    subprocess.call(['chmod', '-R', '777', export_dir])
    print(f"Raw data has been downloaded for batch {batch_name}")

if __name__ == "__main__":
    # download_from_azure(batch_name)
    download_from_nfs(batch_name, username)