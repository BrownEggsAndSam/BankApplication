
h1. EDG Glossary Comparison Tool FAQ

h2. Overview

Purpose:
The EDG Glossary Comparison Tool automates the process of comparing different snapshots of your data glossary (Excel files) to track changes over time. It identifies new attributes, modifications, and consolidates all differences into clear, actionable reports.

Key Features:

Cleans input data by stripping trailing/leading spaces from both column names and cell values.

Performs a left‑merge comparison using “Attribute Registry ID” as the key.

Consolidates multiple changes into a single record per attribute in the Excel report.

Generates a detailed text report with line-by-line change details.

h2. Installation & Folder Structure

Required Folders:

backend: Contains backend.xlsx, which holds column rename mappings.

input: Place your glossary snapshot Excel files here.

output: Reports (Excel and text) are saved to this folder.

Dependencies:

Python 3.x

Pandas

Tkinter (usually included with Python)

Setup:
Ensure the folder structure is maintained as described. Adjust paths in the script if your repository structure differs.

h2. How It Works

Data Loading & Cleaning:
The tool reads Excel files from the input folder. It checks for a “Data Glossary” sheet or uses alternative expected columns, then strips any trailing/leading whitespace to prevent matching errors.

Comparison Logic:
Using the “Attribute Registry ID” as the key, the tool performs a left merge between the current and reference snapshots.

If no matching record exists in the reference, the attribute is marked as “New attribute added.”

For matching records, each field is compared, and any differences are noted.
All differences for a given attribute are consolidated into a single “Tool Comments” field.

Reporting:

Excel Report: One record per attribute with consolidated change details (internal columns like _merge and diff_details are dropped).

Text Report: Organized into sections by field, with each line showing the attribute ID and details of the change (e.g., “Attr Registry ID - Changed from ‘old’ to ‘new’”).

h2. Running the Tool

Launch the script (e.g., edg_comparison.py).

A Tkinter UI window (750x600) will appear:

Use the Browse buttons to select the EDG Reference and Current files.

Click Run Comparison.

The tool processes the files and provides real‑time status updates.

Upon completion, reports are saved to the output folder with filenames that include the current timestamp.

h2. Comparing Multiple Snapshots

Approach:
To monitor changes over time, place all snapshot files in a dedicated folder and use a pairwise (or cumulative) comparison strategy.

Pairwise Comparison: Compare each snapshot with the next (e.g., Snapshot1 vs. Snapshot2, then Snapshot2 vs. Snapshot3, etc.).

Cumulative Comparison: Compare each snapshot against a baseline snapshot to see the overall evolution.

Reporting:
Generate individual reports for each comparison or merge results into a master report with clear timestamp labels for each snapshot pair.

h2. Troubleshooting & FAQs

Trailing Spaces Issues:
If you encounter errors due to trailing spaces, the tool automatically cleans the data by stripping whitespace from both column headers and cell values.

Error Messages:
Errors during file reading (e.g., missing required columns) are reported via the UI. Verify that your files conform to the expected format and folder structure.

Further Questions:
If you experience issues or have questions about the tool’s functionality, please consult the project documentation or reach out to the project maintainers.

h2. Support & Contact

Project Maintainers:
For further assistance, please contact the project team at [email@example.com] or use the project issue tracker.

Additional Documentation:
More detailed developer and user documentation is available in the project’s docs folder.

