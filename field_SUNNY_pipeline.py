#import cv2
import glob
import json
import ntpath
import os
import signal
import subprocess
import sys
import time

#from detectclass import YoloDetectClass
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


executor = ThreadPoolExecutor(max_workers=12)
futures = []

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

batch_names = None
if (len(sys.argv) > 1):
    batch_names = sys.argv[1:]
    
batch_name = sys.argv[1]

DEVELOP_IMAGES = True
BACKUP_AND_DELETE_LOCAL_DATA = True
UPLOAD_WHEN_COMPLETED = False
FIX_ACCESS_RIGHTS = False


nfs_path = "/mnt/research-projects/r/raatwell/longterm_images3/field-batches/"


def processImage(imagepath,outputdir, profilepath):


    cmd1='./squashfs-root/usr/bin/rawtherapee-cli -p "'+profilepath+'" -a -O "'+outputdir+'" -j99 -js3 -Y -c "'+ imagepath+'"' 
    print(cmd1)
    os.system(cmd1)
    

def develop_images(batch_name):
    #dev_im_input_path1 = Path("/home/psa_images/temp_data/field_data/") / str(batch_name) / "raws"
    dev_im_input_path2 = Path("/home/psa_images/temp_data/field_data/") / str(batch_name) / 'raws' / "**"
    dev_im_input_paths = [dev_im_input_path2]
    for dev_im_input_path in dev_im_input_paths:
        #print("1")
        # remove jpg images from the raw folder
        for zippath in glob.iglob(str(dev_im_input_path / Path("*.JPG"))):
            os.remove(zippath)
        #print(str(dev_im_input_path / Path("*.pp3")))
        #print(glob.glob(str(dev_im_input_path / Path("*.pp3"))))
        list_of_pp3_files = glob.glob(str(dev_im_input_path / Path("*.pp3")))
        #print(len(list_of_pp3_files))
        if(len(list_of_pp3_files)>0):
            #dev_im_output_path = Path("/mnt/research-projects/r/raatwell/longterm_images3/field-batches/") / str(batch_name) / "developed-images/"
            dev_im_output_path = Path("/home/psa_images/temp_data/field_data/") / str(batch_name) / "developed-images/"
            #dev_im_development_profile_path = Path("/home/psa_images/persistent_data/semifield-utils/image_development/dev_profiles/") / (str(batch_name)+".pp3")
            #print("2")
            #assert (os.path.exists(dev_im_development_profile_path))
            
            os.makedirs(dev_im_output_path, exist_ok = True)
            
            for pp3_file in list_of_pp3_files:
                #print("3")
                image_path = pp3_file[:-4]
                print("Processing file..")
                print(image_path)
                
                a = executor.submit(processImage, str(image_path),str(dev_im_output_path), str(pp3_file))
                #processImage(str(image_path),str(dev_im_output_path), str(pp3_file))
            
            #exe_command = f"./RawTherapee_5.10.AppImage --cli \
            #    -O {dev_im_output_path} \
            #    -p {dev_im_development_profile_path} \
            #    -j99 \
            #    -c {dev_im_input_path}"
            #exe_command2 = 'bash -c "OMP_NUM_THREADS=90; ' + exe_command + '"'
            
            #print(exe_command2)
            #try:
            #    # Run the rawtherapee command
            #    #subprocess.run(exe_command, shell=True, check=True)
            #    subprocess.run(exe_command2, shell=True, check=True)
            #    print("")
            #except Exception as e:
            #    raise e
                
    while executor._work_queue.qsize():
        print('Queue size: '+str(executor._work_queue.qsize()))
        time.sleep(2)
    time.sleep(5)
    src = str(Path("/home/psa_images/temp_data/field_data/") / str(batch_name))
    subprocess.call(['chmod', '-R', '777', src])
    
    executor.shutdown(wait=True)              
            
    print("Image development has finished for batch " + str(batch_name))
    
    #print("Uploading rawtherapee development profiles to azure..")
    #dev_im_development_profile_path = Path("/home/psa_images/persistent_data/semifield-utils/image_development/dev_profiles/") / (str(batch_name)+".pp3")
    #exe_command = f"/home/psa_images/semifield_tools/azcopy copy \
    #    {dev_im_development_profile_path} \
    #    'SAS_key_here' \
    #    --recursive \
    #    --overwrite=true"
        
    #print(exe_command)
    #try:
    #    process_id = subprocess.run(exe_command, shell=True, check=True)
    #except Exception as e:
    #    raise e
    #os.killpg(os.getpgid(process_id.pid), signal.SIGKILL)
    #process_id.wait()
    #print("Profile has been uploaded for batch " + str(batch_name))

def upload_to_azure(batch_name):
    time.sleep(30)
    export_dir = "/home/psa_images/temp_data/semifield-outputs/" + str(batch_name)
    exe_command = f"/home/psa_images/semifield_tools/azcopy copy \
        {export_dir} \
        'SAS_key_here' \
        --recursive \
        --overwrite=true"
        
    print(exe_command)
    try:
        # Run the rawtherapee command
        #subprocess.run(['/bin/bash', '-i', '-c', exe_command])
        #process_id = subprocess.run(exe_command, shell=True, check=True)
        process_id = subprocess.run(exe_command, shell=True, check=True)
        #subprocess.check_output(['/home/psa_images/semifield_tools/azcopy', 'copy', export_dir, 'SAS_key_here', '--recursive', '--overwrite=true'])
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
        #subprocess.run(['/bin/bash', '-i', '-c', exe_command])
        #process_id = subprocess.run(exe_command, shell=True, check=True)
        process_id = subprocess.run(exe_command, shell=True, check=True)
        #subprocess.check_output(['/home/psa_images/semifield_tools/azcopy', 'copy', export_dir, 'SAS_key_here', '--recursive', '--overwrite=true'])
        print("")
    except Exception as e:
        print("")
    
    #os.killpg(os.getpgid(process_id.pid), signal.SIGKILL)
    #process_id.wait()
    print("Weed detection has finished for batch " + str(batch_name))

def move_local_data_to_NSF(batch_name):
    dev_im_input_path1 = str(Path("/home/psa_images/temp_data/field_data/") / str(batch_name))
    src = dev_im_input_path1
    dest = nfs_path
    #subprocess.call('rsync --remove-source-files -h ' + src + ' ' + dest)
    #subprocess.Popen(['rsync', '-avzh', '--remove-source-files', '--progress', src, dest])
    subprocess.call(['rsync', '-avzh', '--remove-source-files', '--progress', src, dest])
    
    subprocess.call(['chmod', '-R', '777', dest])
  
    
def update_access_rights():

    src = "/home/psa_images/temp_data"
    #subprocess.Popen(['chmod', '-R', '777', src])
    subprocess.call(['chmod', '-R', '777', src])
    
    time.sleep(10)


if(DEVELOP_IMAGES):
    if(batch_names is not None):
        for batch_name in batch_names:
            develop_images(batch_name)
    else:
        develop_images(batch_name)
if(UPLOAD_WHEN_COMPLETED):
    upload_to_azure(batch_name)
if(FIX_ACCESS_RIGHTS):
    update_access_rights()
if(BACKUP_AND_DELETE_LOCAL_DATA):
    move_local_data_to_NSF(batch_name)
    
