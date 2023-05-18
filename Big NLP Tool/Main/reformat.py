import pandas as pd
from pathlib import Path

def read_excel_files(input_file, abbreviations_file):
    input_df = pd.read_excel(input_file)
    abbreviations = pd.read_excel(abbreviations_file)
    return input_df, abbreviations

def reformat_attribute_names(input_df, abbreviations):
    abbreviation_dict = dict(zip(abbreviations['Word'], abbreviations['Abbreviation']))
    input_df['Physical Name'] = input_df['Attribute Name'].apply(
        lambda x: '_'.join([abbreviation_dict.get(word, word) for word in x.split()])
    )
    return input_df

def main(input_file, abbreviations_file, output_file):
    print("Reading Excel files...")
    input_df, abbreviations = read_excel_files(input_file, abbreviations_file)

    print("Reformatting input Attribute Names into Physical Names...")
    output_df = reformat_attribute_names(input_df, abbreviations)

    print("Saving processed data to output file...")
    output_df.to_excel(output_file, index=False)

    print("Process completed.")

file_path = './Big NLP Tool/Main/'
abbreviations_file = file_path + "Abbreviations.xlsx"
input_file = file_path + "input.xlsx"
output_file = file_path + "Output_Physical_Names.xlsx"

main(input_file, abbreviations_file, output_file)
