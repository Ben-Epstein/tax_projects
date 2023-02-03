#!/usr/bin/env python3

import os
import pandas as pd
from tqdm import tqdm
import shutil
from glob import glob
from time import sleep
from pathlib import PureWindowsPath


def get_file():
    cpa_file = PureWindowsPath(input(
        "Please provide the full path and file name to the CPA Tax Spreadsheet: "
    ))
    try:
        df = pd.read_csv(cpa_file, encoding="cp1252")
        return df
    except Exception as e:
        print(
            "There was an issue opening the file. Let's try again. See error below",
        )
        print(e)
        return get_file()
       
        
def get_clients(output_loc, cur_year):
    print("Inspecting client folders")
    try:
        all_clients = glob(f"{output_loc}/**/*{cur_year}/", recursive=True)
        return all_clients
    except Exception as e:
        print(f"There was an issue inspecting the clients: {e}")
        sleep(5)
        raise


def convert_and_copy():
    file_loc = PureWindowsPath(
        input("Please provide the full path to the input files: ")
    )
    output_loc = PureWindowsPath(
        input(
            "Please provide the full path the final output folder. "
            "All CPA folders should be here: "
        )
    )
    cur_year = input(
        "What year are we filing in? This number should match the year of the folder "
        "we are adding the files to "
        "(For example, in year 2022 filing taxes for 2021, enter 2022): "
    )
    
    print("-"*50)
    print("Input location:", file_loc)
    print("Output location:", output_loc)
    print("Current year filing:", cur_year)
    print("-"*50)
    correct = input("Is this information correct? [Y]/n ") or "Y"
    if correct.upper() != "Y":
        return convert_and_copy()
    

    must_be_pdf = True
    fnames = os.listdir(file_loc)
    full_files = [f"{file_loc}/{file}" for file in fnames]
    print(f"Found {len(full_files)} in {file_loc}:", full_files)
    all_files = [fname for fname, file in zip(fnames, full_files) if os.path.isfile(file)]
    print(f"Validated {len(all_files)} remaining:", all_files)

    if must_be_pdf:
        all_files = [file for file in all_files if file.endswith("pdf")]

    # Mapping data for account numbers to CPA data
    cpa_cols = ["Tax Info Recipient 1", "Tax Info Recipient 2"]
    client_col = "Household: Account Name"
    acct_num_col = "Financial Account: Financial Account Name"
    custodian_name = "Custodian"
    household_id = "Household: Source System ID"

    cols = cpa_cols + [client_col, acct_num_col, custodian_name, household_id]

    # Mapping data for financial account number to household number
    account_to_household_key = acct_num_col
    account_to_household_value = household_id
    mapping_cols = [account_to_household_key, account_to_household_value]

    all_cols = list(set(cols + mapping_cols))

    df = get_file()[all_cols]
    df = df[df[custodian_name] == "Charles Schwab & Co."]

    # Mapping data for financial account number to household number
    household_mapping = df[mapping_cols].copy()
    household_mapping = household_mapping.set_index(
        account_to_household_key
    ).to_dict()[account_to_household_value]
    # Grab the last 2-4 digits of the household ID
    household_mapping = {k: str(v).split("-")[-1] for k, v in household_mapping.items()}

    # Clean up unicode char (\xa0)
    df = df.fillna("None")
    for c in cpa_cols:
        df[c] = df[c].apply(lambda row: row.strip())

    print(f"Processing {len(all_files)} files")

    all_clients = get_clients(output_loc, cur_year)
    print("Found clients")

    # Structure is 1234-5678_rest_of_name.pdf
    # First 8 digits are account #, first 4 must be redacted
    cleaned_files = []
    failed_files = {}
    for file in tqdm(all_files):
        try:
            acct_number, *rest_of_file = file.split("_")
            acct_number = acct_number.replace("-", "")
            rest_of_file = "_".join(rest_of_file)
            redacted_acct_number = "X" * 4 + acct_number[4:]
    
            df_for_acct = df[df[acct_num_col] == acct_number]
            # Somee clients have a "/" in their name, but windows thinks it's a new folder. 
            # So we replace the "/" with "_" for the file name
            client = df_for_acct[client_col].values[0].replace("/", "_")
    
            file_name = f"{client}_{redacted_acct_number}_{rest_of_file}"
    
            household_id = household_mapping[acct_number]
            for client_dir in all_clients:
                household_id_pth = f"_{household_id}\\"
                if household_id_pth in str(client_dir):
                    # This is the right client. Write the file
                    input_file = PureWindowsPath(file_loc) / file
                    output_file = PureWindowsPath(client_dir) / file_name
                    shutil.copyfile(input_file, output_file)
                    cleaned_files.append(file_name)
        except Exception as e:
            failed_files[file] = str(e)
            continue
    return cleaned_files, failed_files

    
if __name__ == "__main__":
    try:
        clean, failed = convert_and_copy()
    except Exception as e:
        print("There was an error running your process")
        print(e)
        print("This window will close in 20 seconds")
        sleep(20)
        raise e
    print(f"Done converting {len(clean)} files!")
    if failed:
        print(f"The following {len(failed)} files failed to be processed:")
        for f in failed:
            print(f, "--", failed[f])
    print("This window will close automatically in 20 seconds")
    sleep(20)
    
