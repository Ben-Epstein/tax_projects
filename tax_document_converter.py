#!/usr/bin/env python3

import os
import pandas as pd
from tqdm import tqdm
import shutil
from glob import glob
from pathlib import PureWindowsPath


def get_file():
    cpa_file = PureWindowsPath(input(
        "Please provide the full path and file name to the CPA Tax Spreadsheet"
    ))
    try:
        df = pd.read_csv(cpa_file, encoding="cp1252")
        return df
    except Exception as e:
        print(
            "There was an issue opening the file. Let's try again. See error below",
        )
        print(e)
        get_file()


def convert_and_copy():
    file_loc = PureWindowsPath(
        input("Please provide the full path to the input files.")
    )
    output_loc = PureWindowsPath(
        input(
            "Please provide the full path the final output folder. "
            "All CPA folders should be here."
        )
    )
    cur_year = input(
        "What year are we filing in? This number should match the year of the folder "
        "we are adding the files to "
        "(For example, in year 2022 filing taxes for 2021, enter 2022)"
    )

    must_be_pdf = True
    all_files = [f"{file_loc}/{file}" for file in os.listdir(file_loc)]
    print(f"Found {len(all_files)} in {file_loc}:", all_files)
    all_files = [file for file in all_files if os.path.isfile(file)]
    print(f"Validated {len(all_files)} remaining:", all_files)

    if must_be_pdf:
        all_files = [file for file in all_files if file.endswith("pdf")]

    # Mapping data for account numbers to CPA data
    cpa_cols = ["Tax Info Recipient 1: Full Name", "Tax Info Recipient 2: Full Name"]
    client_col = "Account Name"
    acct_num_col = "Financial Account Name"
    custodian_name = "Custodian: Custodian Name"
    household_id = "Source System ID"

    cols = cpa_cols + [client_col, acct_num_col, custodian_name, household_id]

    # Mapping data for financial account number to household number
    account_to_household_key = acct_num_col
    account_to_household_value = "Source System ID"
    household_prefix = "Household-"
    mapping_cols = [account_to_household_key, account_to_household_value]

    all_cols = list(set(cols + mapping_cols))

    df = get_file()[all_cols]
    df = df[df[custodian_name] == "Charles Schwab & Co."]

    # Mapping data for financial account number to household number
    household_mapping = df[mapping_cols].copy()
    household_mapping = household_mapping.set_index(
        account_to_household_key
    ).to_dict()[account_to_household_value]

    # Clean up unicode char (\xa0)
    df = df.fillna("None")
    for c in cpa_cols:
        df[c] = df[c].apply(lambda row: row.strip())

    print(f"Processing {len(all_files)} files")

    all_clients = glob(f"{output_loc}/**/*{cur_year}/", recursive=True)

    # Structure is 1234-5678_rest_of_name.pdf
    # First 8 digits are account #, first 4 must be redacted
    cleaned_files = []
    for file in tqdm(all_files):
        acct_number, *rest_of_file = file.split("_")
        acct_number = acct_number.replace("-", "")
        rest_of_file = "_".join(rest_of_file)
        redacted_acct_number = "X" * 4 + acct_number[4:]

        df_for_acct = df[df[acct_num_col] == acct_number]
        client = df_for_acct[client_col].values[0]

        file_name = f"{client}_{redacted_acct_number}_{rest_of_file}"
        cleaned_files.append(file_name)

        household_id = household_mapping[acct_number].lstrip(household_prefix)
        for client_dir in all_clients:
            if household_id in str(client_dir):
                # This is the right client. Write the file
                input_file = PureWindowsPath(file)
                output_file = PureWindowsPath(client_dir) / file_name
                shutil.copyfile(input_file, output_file)

    
if __name__ == "__main__":
    convert_and_copy()
    