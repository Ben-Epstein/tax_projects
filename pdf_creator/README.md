# PDF CC Creator

## Description
This python script created CC pdfs given a csv file containing the relevant account information and HH IDs.

The following columns must be present in the CSV file provided
1. Full Name
2. Statement CC Details
3. HH ID

The program will create a new folder called `results` with a PDF per household ID

## Installing
To use this script, you will need the following:
1. Python >= 3.7. Download [here](https://www.python.org/downloads/)
2. `pip` (pythons package manager). Run `py -m ensurepip --upgrade`
3. Supporting python packages:
   1. `pandas`
   2. `reportlab`

Install these by running `pip install -r pdf_creator/requirements.txt`

## Running
To run this script, double click on the python file, or, from the terminal, run:
`py pdf_creator/pdf_creator.py`

The program will prompt you for the following information:
1. Location of the CC details CSV file

**Please make sure to provide all responses as full paths. They should start with `C:\\` or similar (depending on the drive)**
