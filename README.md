## **Field Preprocessing Workflow**

### **Note: Storage Paths**
- **Short-Term Storage**:
  - Downloaded images are stored temporarily at:
    ```bash
    /home/psa_images/temp_data/field_data/
    ```
- **Long-Term Storage**:
  - Images are transferred to long-term storage at:
    ```bash
    /mnt/research-projects/r/raatwell/longterm_images3/field-batches
    ```

---

### **1. Connect to Sunny**
- SSH into Sunny and navigate to the following directory:
  ```bash
  /home/psa_images/field_tools
  ```

### **2. Download New Image Batch**
- To download a new batch from the Azure field-batches blob container, run the following command:
  ```bash
  python download_raw_batch.py [BATCH_NAME]
  ```
  - Example:
    ```bash
    python download_raw_batch.py AL_2023-10-06
    ```
- The batch will be saved in:
  ```bash
  temp_data/field_data/
  ```

### **3. Open RawTherapee**
- Run RawTherapee using the command:
  ```bash
  ./RawTherapee_5.10.AppImage
  ```
  Note: if you get permission denied error, then first use this command to grant execution:
  ```bash
  chmod u+x RawTherapee_5.10.AppImage
  ```
  then run RawTherapee: 
  ```bash
  ./RawTherapee_5.10.AppImage
  ```
- In the file browser, navigate to the newly downloaded batch and browse the images.

### **4. Apply Processing Profile**
- **Select Representative Color Checker Image**:
  - Click on the color checker image to expand it.

- **Load Profile**:
  - Apply a pre-made profile by right-clicking the selected image:
    - **Right-click** → `Apply` → `My Profile`
  - Alternatively, if right-click isn’t available, use the **Folder** icon in the Processing Profiles tool pane.
  
- **Profiles Path**:
  - Profiles should be stored in your local private user space:
    ```bash
    /home/<your_username>/.config/RawTherapee/profiles
    ```
  - If saving to this path doesn’t work, use the following alternative path:
    ```bash
    /home/<your_username>/.config/RawTherapee-AppImage/profiles
    ```
  
- **Choose Appropriate Profile**:
  - Pick a profile most similar to the site name and date. Alternatively, you can use a profile from any batch as long as it matches the site name and date.

- **Adjust White Balance & Exposure**:
  - After the profile is loaded, adjust white balance using the **"Color"** icon:
    - **Pick** a light or dark gray area (avoid black, white, or very light gray) for white balancing.
  - Adjust exposure compensation if needed.
  
- **Save Profile**:
  - Save the updated profile with the name of the current batch.

### **5. Batch Apply the Profile**
- **Apply Profile to Entire Batch**:
  - **Ctrl + A** → **Right-click** → `Apply Processing Profile Operations` → `Apply` → `My Profiles` → Select your saved profile.
  - If "My Profiles" doesn’t appear, ensure the profile is saved in `RawTherapee-AppImage`.

- **Review and Adjust**:
  - Scroll through the images to check for exposure consistency.
  - For any overexposed images:
    - **Shift + Click** or **Ctrl + Click** to select multiple images.
    - Adjust exposure compensation using the **Exposure** icon.
  
- **.pp3 Files**:
  - Adjustments are automatically saved in `.pp3` files for individual images.

### **6. Preprocessing the Images**
- **Clear Unwanted Profiles**:
  - For images not worth saving, clear the profile:
    **Right-click** → `Processing Profile Operations` → `Apply` → `Clear`.
  - This ensures that no JPEGs are created for those images.

- **Process Subfolders**:
  - Ensure both subfolders (`01` and `02`) are processed. Once both are profiled, run the preprocessing pipeline:
    ```bash
    python field_SUNNY_pipeline.py [BATCH_NAME]
    ```
  - Example:
    ```bash
    python field_SUNNY_pipeline.py AL_2023-10-06
    ```