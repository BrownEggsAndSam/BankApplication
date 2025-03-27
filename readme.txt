import pandas as pd
from datetime import datetime
import os

# Define file paths
package_input_path = './__glossaryMonthlyExtract/input/'
package_output_path = './__glossaryMonthlyExtract/output/'
template_path = os.path.join(package_input_path, 'Template.xlsx')
output_filename = f'Collibra SF EDG Extract {datetime.now().strftime("%m%d%Y")}.xlsx'
output_path = os.path.join(package_output_path, output_filename)
fallout_report = []

def log_and_report(message):
    print(message)
    fallout_report.append(message)

def update_report_facts():
    df = pd.read_excel(template_path, sheet_name='Report Facts')
    df.iloc[4, 2] = datetime.now().strftime("%m/%d/%Y")
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='Report Facts', index=False)
    log_and_report("Updated Report Facts with today's date.")

def process_data_glossary():
    dg = pd.read_excel(os.path.join(package_input_path, 'DG Tab.xlsx'))
    dg_nc = pd.read_excel(os.path.join(package_input_path, 'DG Tab_NC.xlsx'))
    
    if dg.isnull().values.any():
        log_and_report("Null values found in DG Tab.xlsx")
    
    dg_combined = pd.concat([dg, dg_nc], ignore_index=True)
    dg_combined.columns = ["Attribute Name", "Attribute Registry ID", "Definition", "Status", "Last Modified On", "Business Segment", "KDE", "Privacy Designation", "Authoritative Source", "Historical Approved Date", "Domain"]
    
    invalid_attr_ids = dg_combined[~dg_combined['Attribute Registry ID'].str.match(r'ATTR\\d{5}')]
    if not invalid_attr_ids.empty:
        log_and_report(f"Invalid Attribute Registry IDs found: {invalid_attr_ids['Attribute Registry ID'].tolist()}")
    
    dg_unique = dg_combined.groupby('Attribute Registry ID').agg(lambda x: ', '.join(x.unique())).reset_index()
    
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
        dg_unique.to_excel(writer, sheet_name='Data Glossary', index=False)
    log_and_report("Processed Data Glossary and saved unique records.")

def process_ref_values():
    rv = pd.read_excel(os.path.join(package_input_path, 'RV Tab.xlsx'))
    rv_nc = pd.read_excel(os.path.join(package_input_path, 'RV Tab_NC.xlsx'))
    rv_combined = pd.concat([rv, rv_nc], ignore_index=True)
    
    rv_combined.columns = ["Attribute Name", "Full Name", "Reference Value", "Definition", "Short Code", "Business Segment", "Status", "Last Modified On", "Domain"]
    
    invalid_full_names = rv_combined[~rv_combined['Full Name'].str.match(r'ATTR\\d{5}')]
    if not invalid_full_names.empty:
        log_and_report(f"Invalid Full Names found: {invalid_full_names['Full Name'].tolist()}")
    
    rv_combined.drop(columns=['Full Name'], inplace=True)
    
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
        rv_combined.to_excel(writer, sheet_name='Ref Values', index=False)
    log_and_report("Processed Reference Values and saved records.")

def process_sor():
    sor = pd.read_excel(os.path.join(package_input_path, 'SoR_tab.xlsx'))
    sor_filtered = sor[sor['[Technology Asset] system of record for [Business Term] > Domain'].isin(['Enterprise Data Glossary', 'Non Curated - Enterprise Data Glossary'])]
    
    sor_filtered = sor_filtered[[
        '[Technology Asset] system of record for [Business Term] > Name',
        '[Technology Asset] system of record for [Business Term] > Full Name',
        'Name',
        'CMDB Asset ID (No Formatting)',
        'CMDB Asset Status (No Formatting)',
        'CMDB Asset Type (No Formatting)'
    ]]
    
    sor_filtered.columns = ["Attribute Name", "Attribute ID", "Asset Name", "CMDB Asset ID", "CMDB Asset Status", "CMDB Asset Type"]
    
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
        sor_filtered.to_excel(writer, sheet_name='SOR', index=False)
    log_and_report("Processed SOR and saved filtered records.")

def process_kde_controls():
    kde = pd.read_excel(os.path.join(package_input_path, 'KDE Controls View.xlsx'))
    kde_filtered = kde[[
        '[Business Rule] governs [Business Term] > Full Name',
        '[Business Rule] governs [Business Term] > Name',
        'Name',
        '[Business Rule] implemented in [Technology Asset] > Name',
        'Control Certification Owner',
        'Effective Start Date',
        'Full Name',
        'Asset Type',
        'EDQ Rule Id',
        '[FNMA Business Rule] Control belongs to Asset Name [System] > Name'
    ]]
    
    kde_filtered.columns = [
        "Attribute ID", "Attribute Name", "KDE Control Name", "Asset Name", "Control Certification Owner",
        "Effective Start Date", "Full Name", "Asset Type", "EDQ Rule ID", "Control belongs to EDQ Asset"
    ]
    
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
        kde_filtered.to_excel(writer, sheet_name='KDE Controls', index=False)
    log_and_report("Processed KDE Controls and saved records.")

def save_fallout_report():
    with open(os.path.join(package_output_path, 'fallout_report.txt'), 'w') as f:
        f.write("\n".join(fallout_report))
    log_and_report("Fallout report saved.")

def main():
    print("Starting Glossary Extraction Process...")
    update_report_facts()
    process_data_glossary()
    process_ref_values()
    process_sor()
    process_kde_controls()
    save_fallout_report()
    print("Process completed successfully.")

if __name__ == "__main__":
    main()
