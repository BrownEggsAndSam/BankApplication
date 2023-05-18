import pandas as pd
from pathlib import Path

file_path = './Big NLP Tool/Main/'

def read_excel_files(input_file, abbr_file, occurences_file):
    input_df = pd.read_excel(input_file)
    abbr = pd.read_excel(abbr_file)
    occurences = pd.read_excel(occurences_file)
    return input_df, abbr, occurences

def create_abbr_dict(abbr):
    abbr_dict = {}
    for _, row in abbr.iterrows():
        abbr_dict[row['Word']] = row['Abbreviation']
    return abbr_dict

def reformat_attribute_name(attribute_name, abbr_dict):
    words = attribute_name.split()
    physical_name_parts = []

    for word in words:
        if word in abbr_dict:
            physical_name_parts.append(abbr_dict[word])
        else:
            physical_name_parts.append(word)

    return '_'.join(physical_name_parts)

def find_occurrences(physical_name, occurences):
    matches = occurences[occurences['Physical Name'] == physical_name]
    return matches

def create_output_df(input_df, abbr_dict, occurences):
    output_data = []
    for _, row in input_df.iterrows():
        attribute_name = row['Attribute Name']
        physical_name = reformat_attribute_name(attribute_name, abbr_dict)
        matches = find_occurrences(physical_name, occurences)

        for _, match in matches.iterrows():
            output_data.append({
                'Attribute Name': attribute_name,
                'Physical Name': physical_name,
                'Attribute ID & Count': f"{match['Attribute ID']} [{match['Count']}]"
            })

    return pd.DataFrame(output_data)

def main(input_file, abbr_file, occurences_file, output_file):
    input_df, abbr, occurences = read_excel_files(input_file, abbr_file, occurences_file)
    abbr_dict = create_abbr_dict(abbr)
    output_df = create_output_df(input_df, abbr_dict, occurences)
    output_df.to_excel(output_file, index=False)

input_file = Path(file_path + "input.xlsx")
abbr_file = Path(file_path + "Abbreviations.xlsx")
occurences_file = Path(file_path + "Occurences.xlsx")
output_file = Path(file_path + "Output.xlsx")

main(input_file, abbr_file, occurences_file, output_file)
