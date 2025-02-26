 Created: 11-11-2022
 Modified: 26-02-2025
 Author: Rasmus Riis Kristensen
 Name: PDF_Fraud_Check.py
 Usage: Execute the script in a folder containing PDF files. Altered PDF files # will be put in subfolders to each examined folder in a folder named 'Altered files'.
 The script is recursive.
 Usage: Execute the script directly with no arguments in the top folder.
 (python PDS_Fraud_Detector.py) It will then look for PDF files in the folder and subfolders in which the script resides and check if they have been altered# using Adobe Acrobat Pro and extract any old copies. It will Then run EXIFTool analysis on the PDF's. EXIFTool will also have to be placed in the same directory as the script. 
 If run on a Linux machine then the script will have to be changed  accordingly or the part with EXIFTool will have to be commented out

 Remember to open the TSV file with Excel


