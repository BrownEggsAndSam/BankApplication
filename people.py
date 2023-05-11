import pandas as pd

# Load the first Excel file into a pandas DataFrame
df = pd.read_excel('DSETEDL.xlsx')

# Create the 'EDL Indicator' column based on the 'EDL Dataset ?' column
df['EDL Indicator'] = df['EDL Dataset ?'].map({
    'EDL 1.0': 'EDL',
    'EDL 2.0': 'EDL',
    'Non EDL AWS 1.0': 'Not EDL',
    'Non EDL AWS 2.0': 'Not EDL'
})

# Create 'NoEDLStatus' DataFrame for blank 'EDL Dataset ?' and delete from original DataFrame
no_edl_status_df = df[df['EDL Dataset ?'].isna()]
df = df.drop(no_edl_status_df.index)

# Create 'NoATTRID' DataFrame for blank 'Attribute Registry ID' and delete from original DataFrame
no_attrid_df = df[df['Attribute Registry ID'].isna()]
df = df.drop(no_attrid_df.index)

# Create 'DSETCountByAsset' DataFrame
dset_count_by_asset_df = df.groupby(['CMDB Asset Name', 'CMDB Asset ID', 'EDL Indicator']).size().unstack(fill_value=0)
dset_count_by_asset_df.columns = ['DSETs Count ' + col for col in dset_count_by_asset_df.columns]
dset_count_by_asset_df.reset_index(inplace=True)

# Load the second Excel file
edg_df = pd.read_excel('consolidated_EDG.xlsx')

# Create 'EDGNoEDLStatus' DataFrame for 'Authoritative Source' not 'EDL' or 'Not EDL' and delete from original DataFrame
edg_no_edl_status_df = edg_df[~edg_df['Authoritative Source'].isin(['EDL', 'Not EDL'])]
edg_df = edg_df.drop(edg_no_edl_status_df.index)

# Create 'EDGCheckEDL' DataFrame
edg_check_edl_df = edg_df.copy()
edg_check_edl_df['In DSET'] = edg_check_edl_df['Full Name'].isin(df['Attribute Registry ID'])
edg_check_edl_df['EDL Occurrences'] = edg_check_edl_df['Full Name'].map(df[df['EDL Indicator'] == 'EDL']['Attribute Registry ID'].value_counts())
edg_check_edl_df['Not EDL Occurrences'] = edg_check_edl_df['Full Name'].map(df[df['EDL Indicator'] == 'Not EDL']['Attribute Registry ID'].value_counts())
edg_check_edl_df['In EDL'] = edg_check_edl_df['Full Name'].isin(df[df['EDL Indicator'] == 'EDL']['Attribute Registry ID'])
edg_check_edl_df['In EDL'] = edg_check_edl_df['In EDL'].map({True: 'In EDL', False: 'Not In EDL'})

# Save everything into a single workbook
with pd.ExcelWriter('output.xlsx') as writer:
    df.to_excel(writer, sheet_name='Original Data', index=False)
    no_edl_status_df.to_excel(writer, sheet_name='NoEDLStatus', index=False)
    no_attrid_df.to_excel(writer, sheet_name='NoATTRID', index=False)
    dset_count_by_asset_df.to_excel(writer, sheet_name='DSETCountByAsset', index=False)
    edg_no_edl_status_df.to_excel(writer, sheet_name='EDGNoEDLStatus', index=False)
    edg_check_edl_df.to_excel(writer, sheet_name='EDGCheckEDL', index=False)

