import argparse
import glob
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from utils import review_preprocessed_batches

executor = ThreadPoolExecutor(max_workers=12)
futures = []

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))
    
parser = argparse.ArgumentParser(description="Process batches with RawTherapee")
parser.add_argument("batch_names", nargs='+', help="Name(s) of the batch(es) to process")
parser.add_argument("--username", required=True, help="Username for remote server in sunny")
args = parser.parse_args()

batch_names = args.batch_names   # This is now a list of one or more batch names
username = args.username

DEVELOP_IMAGES = False
REVIEW_PREPROCESSED_BATCHES = True
BACKUP_LOCAL_DATA = False
UPLOAD_WHEN_COMPLETED = False
FIX_ACCESS_RIGHTS = False

nfs_path = "/mnt/research-projects/r/raatwell/longterm_images3/field-batches/"

def processImage(imagepath,outputdir, profilepath):
    """
     Process a single image using RawTherapee CLI.
    """
    print("Processing image: %s", imagepath)
    cmd1='LD_LIBRARY_PATH=/lib/x86_64-linux-gnu ./squashfs-root/usr/bin/rawtherapee-cli -p "'+profilepath+'" -a -O "'+outputdir+'" -j99 -js3 -Y -c "'+ imagepath+'"' 
    print("Executing command: %s", cmd1)
    os.system(cmd1)
    
def develop_images(batch_name):
    print("Starting image development for batch " + str(batch_name))
    dev_im_input_path2 = Path("temp_data/") / str(batch_name) / 'raws' / "**"
    dev_im_input_paths = [dev_im_input_path2]
    for dev_im_input_path in dev_im_input_paths:
        # remove jpg images from the raw folder
        for zippath in glob.iglob(str(dev_im_input_path / Path("*.JPG"))):
            os.remove(zippath)
        list_of_pp3_files = glob.glob(str(dev_im_input_path / Path("*.pp3")))

        if(len(list_of_pp3_files)>0):
            dev_im_output_path = Path("temp_data/") / str(batch_name) / "developed-images/"
            os.makedirs(dev_im_output_path, exist_ok = True)

            for pp3_file in list_of_pp3_files:
                #print("3")
                image_path = pp3_file[:-4]
                print("Processing file..")
                print(image_path)
                
                a = executor.submit(processImage, str(image_path),str(dev_im_output_path), str(pp3_file))

    executor.shutdown(wait=True)              
    time.sleep(5)
    src = str(Path("temp_data/") / str(batch_name))
    subprocess.call(['chmod', '-R', '777', src])
            
    print("Image development has finished for batch " + str(batch_name))
    
def upload_to_azure(batch_name):
    print("Uploading data to Azure for batch " + str(batch_name))
    time.sleep(30)
    export_dir = "temp_data/field-outputs/" + str(batch_name)
    exe_command = f"/home/psa_images/semifield_tools/azcopy copy \
        {export_dir} \
        'SAS_key_here' \
        --recursive \
        --overwrite=true"
        
    print(exe_command)
    try:
        # Run the rawtherapee command
        process_id = subprocess.run(exe_command, shell=True, check=True)
        print("")
    except Exception as e:
        #raise e
        print("")
        
    ### repeat to upload failed files ###
    exe_command = f"/home/psa_images/semifield_tools/azcopy copy \
        {export_dir} \
        'SAS_key_here' \
        --recursive \
        --overwrite=false"
        
    print(exe_command)
    try:
        # Run the rawtherapee command
        process_id = subprocess.run(exe_command, shell=True, check=True)
        print("")
    except Exception as e:
        print("")
    
    print("Weed detection has finished for batch " + str(batch_name))

def move_local_data_to_NSF(batch_names, username=username):
    for batch_name in batch_names:
        print("Copying local data to lts for batch " + str(batch_name))
        src = Path("temp_data/") / str(batch_name) / "developed-images"
        dest = f"{username}@sunny.ece.ncsu.edu:/mnt/research-projects/r/raatwell/longterm_images3/field-batches/{batch_name}/"

    print(f"Copying data from {src} to {dest}...")
    subprocess.call(['rsync', '-avzh', '--progress', src, dest])
    print("changing permissions on remote server...")

    # Run chmod command remotely via SSH
    print(f"Changing permissions on remote server: {dest}")
    chmod_command = f"ssh {username}@sunny.ece.ncsu.edu 'chmod -R 777 /mnt/research-projects/r/raatwell/longterm_images3/field-batches/{batch_name}'"
    subprocess.call(chmod_command, shell=True)

def update_access_rights():
    print("Updating access rights for local data")
    src = "temp_data"
    subprocess.call(['chmod', '-R', '777', src])
    time.sleep(10)

if(DEVELOP_IMAGES):
    if(batch_names is not None):
        for batch_name in batch_names:
            develop_images(batch_name)
    else:
        develop_images(batch_names)
if(REVIEW_PREPROCESSED_BATCHES):
    for batch_name in batch_names:
        review_preprocessed_batches.inspect_images(str(batch_name))
if(UPLOAD_WHEN_COMPLETED):
    upload_to_azure(batch_name)
if(FIX_ACCESS_RIGHTS):
    update_access_rights()
if(BACKUP_LOCAL_DATA):
    move_local_data_to_NSF(batch_names, username)
