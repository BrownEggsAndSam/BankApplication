import pandas as pd
from pathlib import Path

file_path = './Big NLP Tool/PQ+CW/'
pq_file = file_path +"PQ.xlsx"
cw_file = file_path + "CW.xlsx"
input_file = file_path + "input.xlsx"

# Read the excel files

pq_df = pd.read_excel(pq_file)
cw_df = pd.read_excel(cw_file)
input_df = pd.read_excel(input_file)

# Extract primary qualifiers and class words from input phrases
input_df['Primary Qualifier'] = input_df['Phrase'].apply(lambda x: x.split()[0] if x else 'N/A')
input_df['Class Word'] = input_df['Phrase'].apply(lambda x: x.split()[-1] if x else 'N/A')
input_df['Secondary Qualifier'] = input_df['Phrase'].apply(lambda x: ' '.join(x.split()[1:-1]) if x and len(x.split()) > 2 else '')

# Check validity of primary qualifiers and class words
valid_pq = set(pq_df['Primary Qualifier'])
valid_cw = set(cw_df['Class Word'])

input_df['Primary Qualifier'] = input_df['Primary Qualifier'].apply(lambda x: x if x in valid_pq else 'N/A')
input_df['Class Word'] = input_df['Class Word'].apply(lambda x: x if x in valid_cw else 'N/A')

# Save the output to a new Excel file
output_file = Path("Output.xlsx")
input_df.to_excel(output_file, index=False)
