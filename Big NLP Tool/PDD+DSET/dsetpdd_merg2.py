import pandas as pd
import time
from pathlib import Path

def read_excel_files(pdd_file, dset_file):
    pdd = pd.read_excel(pdd_file)
    dset = pd.read_excel(dset_file)
    return pdd, dset

def merge_files(pdd, dset):
    pdd = pdd.rename(columns={"PDD ID": "PDD+DSETID"})
    dset = dset.rename(columns={"DSET ID": "PDD+DSETID"})
    return pd.concat([pdd, dset], ignore_index=True)

def filter_valid_invalid_ids(df):
    valid_ids = df['Attribute ID'].str.match(r'ATTR\d{5}$')
    valid_df = df[valid_ids].reset_index(drop=True)
    invalid_df = df[~valid_ids].reset_index(drop=True)
    return valid_df, invalid_df

def count_occurrences(df):
    return df.groupby(['Physical Name', 'Attribute ID']).size().reset_index(name='Count Of Groupings')

def save_files(valid_df, invalid_df, occurrences_file, invalid_file):
    valid_df.to_excel(occurrences_file, index=False)
    invalid_df.to_excel(invalid_file, index=False)

def main(pdd_file, dset_file, occurrences_file, invalid_file):
    start_time = time.time()
    print("Reading Excel files...")
    pdd, dset = read_excel_files(pdd_file, dset_file)

    print("Merging PDD and DSET files...")
    merged_df = merge_files(pdd, dset)

    print("Filtering valid and invalid Attribute IDs...")
    valid_df, invalid_df = filter_valid_invalid_ids(merged_df)

    print("Counting occurrences of unique Physical Name and Attribute ID groupings...")
    valid_df = count_occurrences(valid_df)

    print("Saving occurrences and invalid IDs to Excel files...")
    save_files(valid_df, invalid_df, occurrences_file, invalid_file)

    print("Process completed. Time taken: {:.2f} seconds.".format(time.time() - start_time))

file_path = './Big NLP Tool/PDD+DSET/'
pdd_file = file_path +"PDD.xlsx"
dset_file = file_path + "DSET.xlsx"
occurrences_file = file_path + "Occurrences.xlsx"
invalid_file = file_path + "Invalid_Attribute_IDs.xlsx"

main(pdd_file, dset_file, occurrences_file, invalid_file)