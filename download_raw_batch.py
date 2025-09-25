import os
from pathlib import Path
import shutil 
import sys
import subprocess
from typing import List
from tqdm import tqdm

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

assert (len(sys.argv) > 1)
    
batch_name = sys.argv[1]

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
        #subprocess.run(['/bin/bash', '-i', '-c', exe_command])
        #process_id = subprocess.run(exe_command, shell=True, check=True)
        process_id = subprocess.run(exe_command, shell=True, check=True)
        #subprocess.check_output(['/home/psa_images/semifield_tools/azcopy', 'copy', export_dir, 'SAS_key_here', '--recursive', '--overwrite=true'])
        print("")
    except Exception as e:
        raise e
    #os.killpg(os.getpgid(process_id.pid), signal.SIGKILL)
    #process_id.wait()
    print("Raw data has been downloaded for batch " + str(batch_name))
    subprocess.call(['chmod', '-R', '777', export_dir + str(batch_name)])


def find_unprocessed_files(batch_name: str) -> List[Path]:
    raw_dir = Path("/mnt/research-projects/r/raatwell/longterm_images3/field-batches") / batch_name / "raws"
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