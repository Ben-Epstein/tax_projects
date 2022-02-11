# Tax File Name Converter

## Description
This python script will convert raw (Schwab formatted) tax return
documents into properly named files, and copy them from the source
directory (folder) location to the destination, as  provided by the prompts. 

## Installing
To use this script, you will need the following:
1. Python >= 3.7. Download [here](https://www.python.org/downloads/)
2. `pip` (pythons package manager). Run `py -m ensurepip --upgrade`
3. Supporting python packages:
   1. `pandas`
   2. `tqdm`

Install these by running `pip install -r requirements.txt`

## Running
To run this script, double click on the python file, or, from the terminal, run:
`py tax_document_converter.py`

The program will prompt you for the following information:
1. The input path to the tax PDF files
2. The top level folder containing all CPA and Client folders
3. The tax filing year
4. The path and name of the spreadsheet containing the CPA client information
5. The path and name of the spreadsheet containing the mapping of client ID to household ID

**Please make sure to provide all responses as full paths. They should start with `C:\\` or similar (depending on the drive)**
