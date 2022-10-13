# helper info taken from https://realpython.com/creating-modifying-pdf/#creating-a-pdf-file-from-scratch
from pathlib import PureWindowsPath

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List, Union
import pandas as pd
import os
from time import sleep


CWD = PureWindowsPath(os.getcwd())

def get_cc_df():
    cc_file = PureWindowsPath(
        input(
            "Please provide the full path (including file name) to the CC details CSV:\n"
        )
    )
    try:
        df = pd.read_csv(cc_file)
        df = df.rename(columns={i: i.strip() for i in df.columns})
        df = df[["Full Name", "Statement CC Details", "HH ID"]]
        return df
    except Exception as e:
        print(
            "There was an issue opening the file. Note that the program is "
            "expecting the following columns:\n"
            "'Full Name', 'Statement CC Details', 'HH ID'\n"
            "Let's try again. See error below",
        )
        print(e)
        get_cc_df()


df = get_cc_df()

LEFT_MARGIN = 1.5 * inch
# drawString works from the left and bottom (instead of top), so we need to convert
# 11 inch page, 1.5 from top, 9.5 inch from bottom
TOP_MARGIN = 9.5 * inch
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

os.makedirs("results", exist_ok=True)


def _valid_detail(statement_detail: str) -> bool:
    """Many statement details are nan, we want to check for that"""
    return str(statement_detail) != "nan"

def create_pdf(filename: Union[str, PureWindowsPath], names: List[str]) -> None:
    """Given a file name and list of full names, creates the 'cc' pdf"""
    canvas = Canvas(filename, pagesize=LETTER)
    canvas.setFont("Arial", 11)
    # Draw a string 1.5 inch left and 1.5 inch top
    canvas.drawString(LEFT_MARGIN, TOP_MARGIN, "cc:")

    # Each new name needs to decrease the top margin by 0.25 inch
    top_dec = 0*inch
    for name in names:
        canvas.drawString(LEFT_MARGIN + (0.25*inch), TOP_MARGIN - top_dec, f"{name}")
        top_dec += (0.25*inch)

    canvas.save()


def process_households():
    print("Processing households")
    for hh_id in df["HH ID"].unique():
        if not _valid_detail(hh_id):
            continue
        hh_df = df[df["HH ID"]==hh_id]
        # Full name for PDF is "Full Name" + "Statement CC Details"
        names = hh_df["Full Name"].tolist()
        details = hh_df["Statement CC Details"].tolist()
        # But often "Statement CC Details" is nan. We don't want to include the nans
        names = [
            f"{name} {detail}"
            if _valid_detail(detail)
            else name
            for name, detail in zip(names, details)
        ]
        # "The final series of digits after the second dash is the entire HH (Household) ID number"
        hh_id_num = "_".join(hh_id.split("-")[2:])
        file_name = f"CC_HH_{hh_id_num}.pdf"
        results_path = "results"
        file_path = PureWindowsPath(f"CWD") / results_path / file_name
        create_pdf(file_path, names)

    print(f"Done. All PDF files have been placed in {file_path}. This window will close in 10 seconds")
    sleep(10)
    
process_households()
