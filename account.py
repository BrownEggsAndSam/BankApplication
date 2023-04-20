# Call the edl_delta_hydration function
# Function to generate the report
def generate_report(input_data, reimport_data):
    original_records = len(input_data)
    original_blanks = input_data['Attribute Registry ID'].isnull().sum()
    original_invalids = len(input_data.loc[~input_data['Attribute Registry ID'].str.startswith("ATTR", na=False) & input_data['Attribute Registry ID'].notnull()])
    original_valids = original_records - original_blanks - original_invalids

    reimport_records = len(reimport_data)
    reimport_domain_counts = reimport_data['represents Business Term [Business Term] > Domain'].value_counts().to_dict()
    reimport_invalids = len(reimport_data.loc[reimport_data['Validation_Status'] == 'Not Valid'])
    reimport_replaced = len(reimport_data.loc[reimport_data['Validation_Status'] == 'Invalid replaced by tool'])
    reimport_invalids_post_hydration = reimport_invalids - reimport_replaced
    reimport_domain_counts = reimport_data['represents Business Term [Business Term] > Domain'].value_counts().to_dict()

    report = {
        "Original Records": original_records,
        "  Original Blanks": original_blanks,
        "  Original Invalids": original_invalids,
        "  Original Valids": original_valids,
        "Reimport Records": reimport_records,
        "Reimport Invalids Post Hydration": reimport_invalids_post_hydration
    }
    
    for domain, count in reimport_domain_counts.items():
        report[f"Reimport {domain} Count"] = count

    return report


# Function to save the generated log report to a txt file
def save_report_to_txt(report, output_folder, timestamp, input_file_creation_time, reimport_domain_counts):
    log_file_name = f"delta_hydration_report_{timestamp}.txt"
    log_file_path = os.path.join(output_folder, log_file_name)
    
    
    with open(log_file_path, 'w') as log_file:
        log_file.write(f"Input file creation time: {input_file_creation_time}\n\n")
        
        log_file.write("Pre-processed Metrics:\n")
        for key, value in report.items():
            if key.startswith("Original"):
                log_file.write(f"{key}: {value}\n")
        
        log_file.write("\nHydration Metrics:\n")
        for key, value in report.items():
            if key.startswith("Reimport"):
                log_file.write(f"{key}: {value}\n")
                
        log_file.write("\nDomain Breakdown:\n")
        for domain, count in reimport_domain_counts.items():
            log_file.write(f"  {domain}: {count}\n")        
        
        print(f"Log report saved to {log_file_path}")


input_data, reimport_data = edl_delta_hydration(input_data)

report = generate_report(input_data, reimport_data)
for key, value in report.items():
    print(f"{key}: {value}")


# Call the save_report_to_txt function after generating the report
input_file_creation_time = datetime.fromtimestamp(os.path.getctime(input_file)).strftime("%Y-%m-%d %H:%M:%S")
output_folder = save_report_to_txt(report, output_folder, timestamp, input_file_creation_time)
