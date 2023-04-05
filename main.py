import itertools
from pathlib import Path
import pandas as pd
import time
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import tkinter as tk
from tkinter import filedialog

############SYNONYMS####################

def add_synonyms(synonyms, word, synonym):
    if word not in synonyms:
        synonyms[word] = set()

    if synonym not in synonyms:
        synonyms[synonym] = set()

    synonyms[word].add(synonym)
    synonyms[synonym].add(word)

def create_synonym_dict(file_path):
    df = pd.read_excel(file_path)

    synonyms = {}
    for _, row in df.iterrows():
        word, synonym = row['Word'], row['Synonym']
        add_synonyms(synonyms, word, synonym)

    # Propagate synonyms of synonyms
    updated = True
    while updated:
        updated = False
        for word in synonyms:
            current_synonyms = list(synonyms[word])
            for synonym in current_synonyms:
                new_synonyms = synonyms[synonym] - synonyms[word] - {word}
                if new_synonyms:
                    updated = True
                    synonyms[word].update(new_synonyms)

    # Convert sets to lists and sort
    for word in synonyms:
        synonyms[word] = sorted(list(synonyms[word]))

    return synonyms

def apply_synonyms(df, synonym_dict):
    new_rows = []

    for idx, row in df.iterrows():
        original_row = row.copy()
        original_row['Transformed'] = row['Attribute Name']
        new_rows.append(original_row)

        for col_name in ['Primary Qualifier', 'Class Word']:
            if row[col_name] != '-':
                for word in row[col_name].split():
                    if word in synonym_dict:
                        for synonym in synonym_dict[word]:
                            new_row = row.copy()
                            new_row[col_name + ' Synonym'] = synonym
                            new_phrase = row['Transformed'].replace(word, synonym)
                            new_row['Transformed'] = new_phrase
                            new_rows.append(new_row)

                            # Handle cases where there's a synonym for the other column as well
                            other_col_name = 'Class Word' if col_name == 'Primary Qualifier' else 'Primary Qualifier'
                            if row[other_col_name] != '-':
                                for other_word in row[other_col_name].split():
                                    if other_word in synonym_dict:
                                        for other_synonym in synonym_dict[other_word]:
                                            new_row_2 = new_row.copy()
                                            new_row_2[other_col_name + ' Synonym'] = other_synonym
                                            new_phrase_2 = new_phrase.replace(other_word, other_synonym)
                                            new_row_2['Transformed'] = new_phrase_2
                                            new_rows.append(new_row_2)

    return pd.DataFrame(new_rows)

def get_wordnet_pos(word):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV,
    }

    return tag_dict.get(tag, wordnet.NOUN)

def process_files(pq_file, cw_file, input_file, output_file, synonyms):
    start_time = time.time()
    print(f"Step 1: Reading excel files ({time.ctime()})")
    pq_df = pd.read_excel(pq_file)
    cw_df = pd.read_excel(cw_file)
    input_df = pd.read_excel(input_file)
    
    input_df['Attribute Name'] = input_df['Attribute Name'].apply(
    lambda x: ' '.join(
        [lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in nltk.word_tokenize(x)]
        )
    )

    print(f"Step 2: Extracting primary qualifiers and class words ({time.ctime()})")
    input_df['Primary Qualifier'] = input_df['Attribute Name'].apply(lambda x: x.split()[0] if x else '-')
    input_df['Class Word'] = input_df['Attribute Name'].apply(lambda x: x.split()[-1] if x else '-')
    input_df['Secondary Qualifier'] = input_df['Attribute Name'].apply(lambda x: ' '.join(x.split()[1:-1]) if x and len(x.split()) > 2 else '-')

    print(f"Step 3: Checking validity of primary qualifiers and class words ({time.ctime()})")
    valid_pq = set(pq_df['Primary Qualifier'])
    valid_cw = set(cw_df['Class Word'])

    input_df['Primary Qualifier'] = input_df['Primary Qualifier'].apply(lambda x: x if x in valid_pq else '-')
    input_df['Class Word'] = input_df['Class Word'].apply(lambda x: x if x in valid_cw else '-')


    print(f"Step 4: Applying synonyms to input DataFrame ({time.ctime()})")
    input_df['Transformed'] = input_df['Attribute Name']
    # input_df = apply_synonyms(input_df, synonyms, 'Primary Qualifier')
    # input_df = apply_synonyms(input_df, synonyms, 'Class Word')
    input_df = apply_synonyms(input_df, synonym_dict)


    print(f"Step 5: Saving output to a new Excel file ({time.ctime()})")
    input_df.reset_index(drop=True, inplace=True)
    input_df.fillna('-', inplace=True)
    input_df.to_excel(output_file, index=False)

    print(f"Process completed. Time taken: {time.time() - start_time:.2f} seconds.")

    return input_df

#REOCCURANCE#PHYSICALNAMES################################

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
    #print(physical_name)
    matches = occurences[occurences['Physical Name'] == physical_name]
    #print(matches)
    return matches

def create_output_df(input_df, abbr_dict, occurences):
    output_data = []
    for _, row in input_df.iterrows():
        attribute_name = row['Transformed']
        physical_name = reformat_attribute_name(attribute_name, abbr_dict)
        matches = find_occurrences(physical_name, occurences)

        base_row_data = row.to_dict()
        
        if not matches.empty:
            for _, match in matches.iterrows():
                row_data = {
                    'Attribute Name': attribute_name,
                    'Physical Name': physical_name,
                    'Attribute ID & Count': f"{match['Attribute ID']} [{match['Count']}]"
                }
                row_data.update(base_row_data)
                output_data.append(row_data)
        else:
            row_data = {
                'Attribute Name': attribute_name,
                'Physical Name': physical_name,
                'Attribute ID & Count': '-'
            }
            row_data.update(base_row_data)
            output_data.append(row_data)

    return pd.DataFrame(output_data)

####################################TINKER
def run_nlp_tool():
    main(processed_df, abbr_file, occurences_file, output_file)# Replace this with the function that runs your script
    result_label.config(text="Processing complete!")




####################################



def main(input_df, abbr_file, occurences_file, output_file):
    abbr, occurences = pd.read_excel(abbr_file), pd.read_excel(occurences_file)
    abbr_dict = create_abbr_dict(abbr)
    output_df = create_output_df(input_df, abbr_dict, occurences)
    output_df.to_excel(output_file, index=False)


lemmatizer = WordNetLemmatizer()
file_path = './Big NLP Tool/Synonyms/Synonyms.xlsx'
synonym_dict = create_synonym_dict(file_path)
file_path = './Big NLP Tool/PQ+CW/'
pq_file = file_path + "PQ.xlsx"
cw_file = file_path + "CW.xlsx"
input_file = file_path + "input.xlsx"
output_file = Path("pqcwsyn15.xlsx")

processed_df = process_files(pq_file, cw_file, input_file, output_file, synonym_dict)


file_path = './Big NLP Tool/Main/'
abbr_file = Path(file_path + "Abbreviations.xlsx")
occurences_file = Path(file_path + "Occurences.xlsx")

def open_file_and_process():
    file_path = filedialog.askopenfilename()
    if file_path:
        pq_file = './Big NLP Tool/PQ+CW/PQ.xlsx'
        cw_file = './Big NLP Tool/PQ+CW/CW.xlsx'
        input_file = file_path
        output_file = Path("pqcwsyn15.xlsx")

        processed_df = process_files(pq_file, cw_file, input_file, output_file, synonym_dict)

        abbr_file = Path('./Big NLP Tool/Main/Abbreviations.xlsx')
        occurences_file = Path('./Big NLP Tool/Main/Occurences.xlsx')
        output_file = Path("final_output.xlsx")

        main(processed_df, abbr_file, occurences_file, output_file)
        result_label.config(text="Processing complete!")

root = tk.Tk()
root.title("Upload File and Process")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

upload_button = tk.Button(frame, text="Upload File", command=open_file_and_process)
upload_button.pack()

result_label = tk.Label(frame, text="")
result_label.pack()

root.mainloop()

##############


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

