import os
import pandas as pd
from datetime import datetime

# Read input data
print("Reading input data...")
input_file = 'input_file.xlsx'
input_data = pd.read_excel(input_file)

# Consolidate EDG
print("Consolidating EDG...")
def consolidate_edg():
    files = ['EDG.xlsx', 'NewSF.xlsx', 'NC.xlsx', 'InA.xlsx']
    input_folder = os.path.join('_theStewardshipTool','input_data', 'Consolidated_EDG')

    data_frames = []
    for file in files:
        file_path = os.path.join(input_folder, file)
        df = pd.read_excel(file_path)
        data_frames.append(df)

    consolidated_EDG = pd.concat(data_frames, ignore_index=True)

    # Save consolidated_EDG to an Excel file
    output_folder = 'output'
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, 'consolidated_EDG.xlsx')
    consolidated_EDG.to_excel(output_file, index=False)

    print(f"Successfully consolidated EDG. Output saved to {output_file}")
    
    return consolidated_EDG

consolidated_EDG = consolidate_edg()

# DSET and PDD occurrences
print("Processing DSET and PDD occurrences...")
def dset_pdd_occurrences():
    input_folder = os.path.join('_theStewardshipTool','input_data', 'DSET_PDD')
    dset_path = os.path.join(input_folder, 'DSET.xlsx')
    pdd_path = os.path.join(input_folder, 'PDD.xlsx')
    dset = pd.read_excel(dset_path)
    pdd = pd.read_excel(pdd_path)

    merged = pd.concat([dset, pdd])
    merged = merged[['Name', 'represented by [Business Term] > Full Name']]
    merged.columns = ['Physical_Name', 'Attribute_ID']
    merged['Occurrence_Count'] = merged.groupby(['Physical_Name', 'Attribute_ID'])['Physical_Name'].transform('count')

    merged = merged.drop_duplicates()
    merged.to_excel(os.path.join(input_folder, 'DSET_PDD_Occurrences.xlsx'), index=False)

    return merged

DSET_PDD_Occurrences = dset_pdd_occurrences()

# Generate EDL Delta Hydration report
def edl_delta_hydration(input_data):
    print("Copying input data...")
    reimport_data = input_data.copy()
    reimport_data = reimport_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    reimport_data['Validation_Status'] = ''

    # Add new columns to reimport_data DataFrame
    reimport_data['represents Business Term [Business Term] > Name'] = ''
    reimport_data['represents Business Term [Business Term] > Full Name'] = ''
    reimport_data['represents Business Term [Business Term] > Asset Type'] = ''
    reimport_data['represents Business Term [Business Term] > Community'] = ''
    reimport_data['represents Business Term [Business Term] > Domain Type'] = ''
    reimport_data['represents Business Term [Business Term] > Domain'] = ''

    invalid_df = pd.DataFrame(columns=reimport_data.columns)
    dupes_df = pd.DataFrame(columns=reimport_data.columns)
    invalid_df['Replaced_ID'] = ''
    invalid_df['Replaced_By_Name'] = ''

    print("Starting data validation...")
    for index, row in reimport_data.iterrows():
        attr_id = row['Attribute Registry ID']
        name = row['Name']
        if pd.isnull(attr_id):
            dset_pdd_matches = DSET_PDD_Occurrences[DSET_PDD_Occurrences['Physical_Name'] == name]
            if len(dset_pdd_matches) == 1:
                attr_id = dset_pdd_matches.iloc[0]['Attribute_ID']
                reimport_data.at[index, 'Attribute Registry ID'] = attr_id
            elif len(dset_pdd_matches) > 1:
                dupes = []
                for _, match in dset_pdd_matches.iterrows():
                    match_attr_id = match['Attribute_ID']
                    match_attr_name = consolidated_EDG.loc[consolidated_EDG['Full Name'] == match_attr_id, 'Name'].values[0]
                    dupes.append(f"({match_attr_id}) - {match_attr_name}")
                dupes_string = ";\n".join(dupes)
                reimport_data.at[index, 'Attribute Registry ID'] = dupes_string
                row['Attribute Registry ID'] = dupes_string  # Update the 'Attribute Registry ID' column in the dupes_df
                row['Row_Number'] = index + 1
                dupes_df = dupes_df.append(row)
                reimport_data.at[index, 'Validation_Status'] = 'Check duplicate records sheet'
                continue

        if not pd.isnull(attr_id):
            is_valid = (str(attr_id).startswith('ATTR') and str(attr_id)[4:].isdigit() and len(str(attr_id)) == 9) or (str(attr_id).isdigit() and len(str(attr_id)) == 5)
        else:
            continue

        if not is_valid:
            row['Row_Number'] = index + 1
            invalid_df = invalid_df.append(row)
            reimport_data.at[index, 'Validation_Status'] = 'Not Valid'
            original_attr_id = row['Attribute Registry ID']

            # Clear the record and try to see if there is a match using the look up with pdd_dset
            reimport_data.at[index, 'Attribute Registry ID'] = ''
            dset_pdd_matches = DSET_PDD_Occurrences[DSET_PDD_Occurrences['Physical_Name'] == name]
            if len(dset_pdd_matches) == 1:
                new_attr_id = dset_pdd_matches.iloc[0]['Attribute_ID']
                reimport_data.at[index, 'Attribute Registry ID'] = new_attr_id
                reimport_data.at[index, 'Validation_Status'] = 'Invalid replaced by tool'
                # Append the new value it was replaced by
                invalid_df.at[row['Row_Number'] - 1, 'Replaced_ID'] = new_attr_id
                # Get the 'Name' of the 'Replaced_By' attribute from the consolidated EDG
                replaced_by_name = consolidated_EDG.loc[consolidated_EDG['Full Name'] == new_attr_id, 'Name'].values[0]
                invalid_df.at[row['Row_Number'] - 1, 'Replaced_By_Name'] = replaced_by_name
            else:
                reimport_data.at[index, 'Validation_Status'] = 'Not Valid'
                invalid_df.at[row['Row_Number'] - 1, 'Replaced_ID'] = ''
                invalid_df.at[row['Row_Number'] - 1, 'Replaced_By_Name'] = ''
        else:
            if reimport_data.at[index, 'Validation_Status'] != 'Invalid replaced by tool':
                reimport_data.at[index, 'Validation_Status'] = 'Valid'

        attr_id = reimport_data.at[index, 'Attribute Registry ID']
        match = consolidated_EDG[consolidated_EDG['Full Name'] == attr_id]
        if len(match) > 0:
            reimport_data.at[index, 'represents Business Term [Business Term] > Name'] = match.iloc[0]['Name']
            reimport_data.at[index, 'represents Business Term [Business Term] > Full Name'] = match.iloc[0]['Full Name']
            reimport_data.at[index, 'represents Business Term [Business Term] > Asset Type'] = match.iloc[0]['Asset Type']
            reimport_data.at[index, 'represents Business Term [Business Term] > Community'] = match.iloc[0]['Community']
            reimport_data.at[index, 'represents Business Term [Business Term] > Domain Type'] = match.iloc[0]['Domain Type']
            reimport_data.at[index, 'represents Business Term [Business Term] > Domain'] = match.iloc[0]['Domain']

    # Save the output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_file_name = os.path.basename(input_file).split('.')[0]
    output_folder = os.path.join(os.getcwd(), 'output', 'deltaHydration')
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, f"{input_file_name}_{timestamp}.xlsx")
    reimport_data = reimport_data[~reimport_data['Validation_Status'].isin(['Check duplicate records sheet', '', 'Not Valid'])]
    
    print("Generating output file...")
    with pd.ExcelWriter(output_file_path) as writer:
        input_data.to_excel(writer, sheet_name="Original", index=False)
        reimport_data.to_excel(writer, sheet_name="Reimport", index=False)

        if not invalid_df.empty:
            invalid_df.drop('Validation_Status', axis=1).to_excel(writer, sheet_name="Invalid Records", index=False)

        if not dupes_df.empty:
            dupes_df_mod = dupes_df.copy()
            dupes_df_mod.drop(['Validation_Status'], axis=1).to_excel(writer, sheet_name="Dupes", index=False)

    print("Output file generated successfully.")
    return input_data, reimport_data

# Call the edl_delta_hydration function
def generate_report(input_data, reimport_data):
    report = {}

    report['Original Records'] = len(input_data)
    report['Blank Records (Original)'] = input_data['Attribute Registry ID'].isnull().sum()
    report['Valid Attributes (Original)'] = input_data['Attribute Registry ID'].apply(lambda x: (str(x).startswith('ATTR') and str(x)[4:].isdigit() and len(str(x)) == 9) or (str(x).isdigit() and len(str(x)) == 5)).sum()
    report['Invalid Attributes (Original)'] = report['Original Records'] - (report['Blank Records (Original)'] + report['Valid Attributes (Original)'])

    report['Valid Attributes (Reimport)'] = (reimport_data['Validation_Status'] == 'Valid').sum()
    report['Invalid Attributes'] = (reimport_data['Validation_Status'] == 'Not Valid').sum()
    report['Invalid Replaced by Rehydration'] = (reimport_data['Validation_Status'] == 'Invalid replaced by tool').sum()
    report['Exact Matches DSET_PDD'] = reimport_data['Attribute Registry ID'].apply(lambda x: (str(x).startswith('ATTR') and str(x)[4:].isdigit() and len(str(x)) == 9) or (str(x).isdigit() and len(str(x)) == 5)).sum() - report['Valid Attributes (Reimport)']
    report['Duplicate Matches DSET_PDD'] = (reimport_data['Validation_Status'] == 'Check duplicate records sheet').sum()
    report['Blank Records (Reimport)'] = reimport_data['Attribute Registry ID'].isnull().sum()

    return report



input_data, reimport_data = edl_delta_hydration(input_data)

report = generate_report(input_data, reimport_data)
for key, value in report.items():
    print(f"{key}: {value}")

