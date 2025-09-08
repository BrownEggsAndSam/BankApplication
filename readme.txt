import pandas as pd
import os

# File paths
package_input_path = './_csvCleaner/input/'
package_output_path = './_csvCleaner/output/'

# File names
input_file = 'input.csv'
output_file = 'output_cleaned.csv'

# Ensure output folder exists
os.makedirs(package_output_path, exist_ok=True)

# Load CSV
df = pd.read_csv(package_input_path + input_file, dtype=str)

# Replace blanks and "null" (case insensitive) with literal "NULL"
df = df.applymap(lambda x: "NULL" if (pd.isna(x) or str(x).strip() == "" or str(x).strip().lower() == "null") else x)

# Save cleaned CSV
df.to_csv(package_output_path + output_file, index=False)
