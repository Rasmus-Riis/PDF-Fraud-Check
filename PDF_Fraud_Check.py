###########################################################################################
#
# Author: Rasmus Riis Kristensen
# Contact: rrk001@politi.dk
# Name: PDF_Fraud_Check.py
# Usage: Execute the script in a folder containing PDF files. Altered PDF files
# will be put in subfolders to each examined folder in a folder named 'Altered files'.
# The script is recursive.
# Created: 11-11-2022
# Modified: 17-02-2025
# Usage: Execute the script directly with no arguments in the top folder.
# (python PDS_Fraud_Detector.py) It will then look for PDF files in the
# folder and subfolders in which the script resides and check if they have been altered
# using Adobe Acrobat Pro. The EXIFTool will also have to be placed in the same directory
# as the script. If run on a Linux machine then the script will have to be changed 
# accordingly or the part with EXIFTool will have to be commented out
#
# Remember to open the TSV file with Excel
# Version: 2.3.1
###########################################################################################

import os
import subprocess
import hashlib
from datetime import datetime
import csv

def process_pdf_files(directory):
    """
    Processer PDF-filer i den angivne mappe og dens undermapper.
    """
    filecount = 0  # Tæller antallet af PDF-filer fundet
    Alterations = 0  # Tæller antallet af ændringer fundet
    altered_files_bool = False  # Flag for at angive om der er fundet ændrede filer
    totalAltered = 0  # Tæller antallet af ændrede dokumenter

    # Åbner filen 'filinfo.tsv' i tilføj-til-eksisterende-mode og opretter en writer
    with open('filinfo.tsv', 'a+', newline='') as info:
        writer = csv.writer(info, delimiter='\t')
        headerrow = ["Original file name", "Altered file name", "Path", "Filehash", "Created", "Modified", "EXIFTool output"]
        writer.writerow(headerrow)

    # Går igennem mappen og dens undermapper
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(".pdf"):  # Check for pdf extension
                filecount += 1
                file_path = os.path.join(root, filename)
                filehash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                statinfo = os.stat(file_path)
                create_date = datetime.fromtimestamp(statinfo.st_ctime)
                modified_date = datetime.fromtimestamp(statinfo.st_mtime)

                # Laver exiftool output på den oprindelige fil
                cmd = "./exiftool.exe"
                original_exif_data = subprocess.run([cmd, file_path], capture_output=True, text=True).stdout.strip().replace('\n', chr(10))

                # Skriver information om den oprindelige fil til 'filinfo.tsv'
                with open('filinfo.tsv', 'a+', newline='') as info:
                    writer = csv.writer(info, delimiter='\t')
                    writer.writerow([filename, "", file_path, filehash, create_date, modified_date, original_exif_data])

                # Åbner den oprindelige fil i binær læse-mode
                with open(file_path, 'rb') as f:
                    content = f.read()
                    i = None
                    positions = []
                    while i != -1:
                        i = content.rfind(b'\x25\x25\x45\x4f\x46', 0, i)  # Search for %%EOF
                        if i != -1:
                            positions.append(i)
                    positions.sort()

                    # Hvis der er mere end én %%EOF-sekvens, betyder det at filen har været ændret
                    if len(positions) > 1:
                        altered_files_bool = True
                        altered_dir = os.path.join(root, "Altered_files")
                        if not os.path.exists(altered_dir):
                            os.mkdir(altered_dir)
                        print(f"Found previous version in {filename}")
                        v=0
                        totalAltered +=1

                        # Går igennem hver ændring og udtrækker den til en ny fil
                        for count, i2 in enumerate(positions):
                            if 1000 <= i2 <= len(content) - 500:
                                Alterations += 1
                                v +=1
                                i2 += 5  # Include %%EOF
                                print(f"Found {v} previous version in {filename}")
                                altered_filename = f"{filename}_Offset_{i2}_version_{v}.pdf"
                                output_path = os.path.join(altered_dir, altered_filename)
                                with open(output_path, "wb") as out_file:
                                    out_file.write(content[:i2])
                                filehash_altered = hashlib.md5(open(output_path, 'rb').read()).hexdigest()
                                cmd = "./exiftool.exe"
                                exif_data = subprocess.run([cmd, output_path], capture_output=True, text=True).stdout.strip().replace('\n', chr(10))

                                # Skriver information om den ændrede fil til 'filinfo.tsv'
                                with open('filinfo.tsv', 'a+', newline='') as info:
                                    writer = csv.writer(info, delimiter='\t')
                                    writer.writerow([filename, altered_filename, output_path, filehash_altered, create_date, modified_date, exif_data])

    # Udskriver statistik om antallet af fundne ændringer
    if altered_files_bool:
        print(f"Found {Alterations} alterations in {totalAltered} documents.")
    else:
        print("No alterations found.")

process_pdf_files('.')  # Kald funktionen med den aktuelle mappe som argument