import os
import shutil
import random
import zipfile
import tkinter as tk
from tkinter import filedialog

def select_zip_file():
    """
    Opens a file dialog to select the FDCPUnBGunshotDB-main.zip file.
    Dataset source: https://github.com/pedrogarciafreitas/FDCPUnBGunshotDB
    """
    root = tk.Tk()
    root.withdraw() # Hide the main tkinter window
    file_path = filedialog.askopenfilename(
        title="Select the FDCPUnBGunshotDB-main.zip file",
        filetypes=[("Zip files", "*.zip")]
    )
    return file_path

def get_all_images(folder_path):
    """Recursively finds all image files in subdirectories"""
    image_files = []
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, f))
    return image_files

def process_data():
    # 1. Select Zip File
    zip_path = select_zip_file()
    if not zip_path:
        print("Process cancelled: No file selected.")
        print("Please download the dataset from: https://github.com/pedrogarciafreitas/FDCPUnBGunshotDB")
        return

    base_dir = os.path.dirname(zip_path)
    # Temporary directory for extraction
    extract_path = os.path.join(base_dir, "_temp_extraction_")
    output_root = os.path.join(base_dir, "Gunshot_Dataset_Final")

    # 2. Extract Zip
    print(f"📦 Extracting and analyzing: {zip_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
    except zipfile.BadZipFile:
        print("Error: The selected file is not a valid zip file.")
        return

    # 3. Category Mapping (Original Folder -> Target Class)
    categories = {'ENTRADAS_EQX': 'entrance', 'SAIDAS_EQX': 'exit'}
    
    for src_folder, target_name in categories.items():
        src_path = ""
        # Find the category folder within the extracted contents
        for root, dirs, files in os.walk(extract_path):
            if src_folder in dirs:
                src_path = os.path.join(root, src_folder)
                break
        
        if not src_path:
            continue
            
        all_images = get_all_images(src_path)
        print(f"🚀 Processing {target_name}: {len(all_images)} images found.")
        
        # Shuffle for randomized split
        random.seed(42)
        random.shuffle(all_images)

        n = len(all_images)
        train_idx = int(n * 0.7)
        val_idx = train_idx + int(n * 0.15)

        splits = {
            'train': all_images[:train_idx],
            'val': all_images[train_idx:val_idx],
            'test': all_images[val_idx:]
        }

        for phase, file_paths in splits.items():
            target_dir = os.path.join(output_root, phase, target_name)
            os.makedirs(target_dir, exist_ok=True)
            for f_path in file_paths:
                f_name = os.path.basename(f_path)
                # Prefixing parent folder name to avoid collisions
                parent_folder = os.path.basename(os.path.dirname(f_path))
                dest_name = f"{parent_folder}_{f_name}"
                shutil.copy(f_path, os.path.join(target_dir, dest_name))

    # 4. Cleanup temporary files
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
        print(f"扫 Temporary files cleaned up.")

    print(f"\n✅ Preprocessing Complete!")
    print(f"📂 Dataset organized at: {output_root}")

if __name__ == "__main__":
    process_data()
