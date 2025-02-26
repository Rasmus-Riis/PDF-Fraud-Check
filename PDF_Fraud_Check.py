import os
import subprocess
import hashlib
from datetime import datetime
import csv

def process_pdf_files(directory):
    """
    Processes PDF files in the specified folder and its subfolders.
    """
    filecount = 0  # Counts the number of PDF files found
    Alterations = 0  # Counts the number of alterations found
    altered_files_bool = False  # Flag to indicate if altered files have been found
    totalAltered = 0  # Counts the number of altered documents

    # Opens the file 'filinfo.tsv' in append mode and creates a writer
    with open('filinfo.tsv', 'a+', newline='') as info:
        writer = csv.writer(info, delimiter='\t')
        headerrow = ["Original file name", "Altered file name", "Path", "Filehash", "Created", "Modified", "EXIFTool output"]
        writer.writerow(headerrow)

    # Walks through the folder and its subfolders
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(".pdf"):  # Check for pdf extension
                filecount += 1
                file_path = os.path.join(root, filename)
                filehash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                statinfo = os.stat(file_path)
                create_date = datetime.fromtimestamp(statinfo.st_ctime)
                modified_date = datetime.fromtimestamp(statinfo.st_mtime)

                # Generates exiftool output for the original file
                cmd = "./exiftool.exe"
                original_exif_data = subprocess.run([cmd, file_path], capture_output=True, text=True).stdout.strip().replace('\n', chr(10))

                # Writes information about the original file to 'filinfo.tsv'
                with open('filinfo.tsv', 'a+', newline='') as info:
                    writer = csv.writer(info, delimiter='\t')
                    writer.writerow([filename, "", file_path, filehash, create_date, modified_date, original_exif_data])

                # Opens the original file in binary read mode
                with open(file_path, 'rb') as f:
                    content = f.read()
                    i = None
                    positions = []
                    while i != -1:
                        i = content.rfind(b'\x25\x25\x45\x4f\x46', 0, i)  # Search for %%EOF
                        if i != -1:
                            positions.append(i)
                    positions.sort()

                    # If there is more than one %%EOF sequence, it means the file has been altered
                    if len(positions) > 1:
                        altered_files_bool = True
                        altered_dir = os.path.join(root, "Altered_files")
                        if not os.path.exists(altered_dir):
                            os.mkdir(altered_dir)
                        print(f"Found previous version in {filename}")
                        v = 0
                        totalAltered += 1

                        # Iterates through each alteration and extracts it to a new file
                        for count, i2 in enumerate(positions):
                            if 1000 <= i2 <= len(content) - 500:
                                Alterations += 1
                                v += 1
                                i2 += 5  # Include %%EOF
                                print(f"Found {v} previous version in {filename}")
                                altered_filename = f"{filename}_Offset_{i2}_version_{v}.pdf"
                                output_path = os.path.join(altered_dir, altered_filename)
                                with open(output_path, "wb") as out_file:
                                    out_file.write(content[:i2])
                                filehash_altered = hashlib.md5(open(output_path, 'rb').read()).hexdigest()
                                cmd = "./exiftool.exe"
                                exif_data = subprocess.run([cmd, output_path], capture_output=True, text=True).stdout.strip().replace('\n', chr(10))

                                # Writes information about the altered file to 'filinfo.tsv'
                                with open('filinfo.tsv', 'a+', newline='') as info:
                                    writer = csv.writer(info, delimiter='\t')
                                    writer.writerow([filename, altered_filename, output_path, filehash_altered, create_date, modified_date, exif_data])

    # Prints statistics about the number of alterations found
    if altered_files_bool:
        print(f"Found {Alterations} alterations in {totalAltered} documents.")
    else:
        print("No alterations found.")

process_pdf_files('.')  # Calls the function with the current folder as an argument
