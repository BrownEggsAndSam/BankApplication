import pandas as pd
import time
from pathlib import Path

def read_excel_files(pq_file, cw_file, input_file):
    pq = pd.read_excel(pq_file)
    cw = pd.read_excel(cw_file)
    input_df = pd.read_excel(input_file)
    return pq, cw, input_df

def split_phrase(input_df, pq_set, cw_set):
    input_df['Primary Qualifier'] = input_df['Phrase'].apply(lambda x: x.split()[0] if x.split()[0] in pq_set else 'N/A')
    input_df['Class Word'] = input_df['Phrase'].apply(lambda x: x.split()[-1] if x.split()[-1] in cw_set else 'N/A')
    input_df['Secondary Qualifier'] = input_df['Phrase'].apply(lambda x: ' '.join(x.split()[1:-1]))
    return input_df

def main(pq_file, cw_file, input_file, output_file):
    start_time = time.time()
    print("Reading Excel files...")
    pq, cw, input_df = read_excel_files(pq_file, cw_file, input_file)

    print("Processing input phrases...")
    pq_set = set(pq['Primary Qualifiers'])
    cw_set = set(cw['Class Words'])
    output_df = split_phrase(input_df, pq_set, cw_set)

    print("Saving processed data to output file...")
    output_df.to_excel(output_file, index=False)

    print("Process completed. Time taken: {:.2f} seconds.".format(time.time() - start_time))

pq_file = Path("PQ.xlsx")
cw_file = Path("CW.xlsx")
input_file = Path("Input.xlsx")
output_file = Path("Output.xlsx")

main(pq_file, cw_file, input_file, output_file)
