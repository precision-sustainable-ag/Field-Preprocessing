import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

from tqdm import tqdm

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

assert (len(sys.argv) > 1)
    
batch_name = sys.argv[1]

def find_unprocessed_files(batch_name: str) -> List[Path]:
    # Mount the remote directory 
    assert len(sys.argv) > 2, "Usage: python download_raw_batch.py <batch_name> <username>"
    username = sys.argv[2]
    remote_path = f"{username}@sunny.ece.ncsu.edu:/mnt/research-projects/r/raatwell/longterm_images3/field-batches/{batch_name}/raws"
    local_mount = Path("/tmp/remote_raws_mount") / batch_name
    local_mount.mkdir(parents=True, exist_ok=True)

    # Check if already mounted
    if not any(local_mount.iterdir()):
        subprocess.run(["sshfs", remote_path, str(local_mount), "-o", "reconnect"], check=True)


    # TODO: figure out a way to unmount after processing


    raw_dir = local_mount
    raw_imgs = list(raw_dir.rglob("*.ARW"))

    batch_developed = Path("/mnt/research-projects/r/raatwell/longterm_images3/field-batches") / batch_name / "developed-images"
    developed_imgs = sorted(batch_developed.glob("*.jpg"))
    developed_img_stems = {img.stem for img in developed_imgs}

    unprocessed_files = [img for img in raw_imgs if img.stem not in developed_img_stems]
    return unprocessed_files

def download_from_nfs(batch_name):
    # Path where batch is stored in the NFS-mounted directory
    unprocessed_files = find_unprocessed_files(batch_name)

    if not unprocessed_files:
        print(f"No unprocessed files found for batch {batch_name}. Exiting.")
        return
    
    # Local path to copy data to
    export_dir = Path("temp_data/field_data", batch_name)
    export_dir.mkdir(parents=True, exist_ok=True)

    # Code to copy here

    for src_file in tqdm(unprocessed_files, desc="Copying files"):
        relative_path = src_file.relative_to(src_file.parents[2])  # preserves relative path within batch/raws/
        dest_file = export_dir / relative_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
    # Set permissions if needed
    subprocess.call(['chmod', '-R', '777', export_dir])
    print(f"Raw data has been downloaded for batch {batch_name}")

if __name__ == "__main__":
    # download_from_azure(batch_name)
    download_from_nfs(batch_name)