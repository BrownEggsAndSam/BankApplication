import pandas as pd
import os

# (Other existing functions)

def find_primary_qualifiers(consolidated_edg, primary_qualifiers):
    def find_primary_qualifier(name):
        words = name.split()
        for i in range(1, min(5, len(words) + 1)):
            phrase = " ".join(words[:i])
            match = primary_qualifiers[primary_qualifiers["Primary Qualifier Name"] == phrase]
            if not match.empty:
                return match.iloc[0]

        return None

    records = []
    no_match_records = []

    for _, row in consolidated_edg.iterrows():
        match = find_primary_qualifier(row["Name"])

        if match is not None:
            records.append({
                "Name": row["Name"],
                "Primary Qualifier": match["Primary Qualifier Name"],
                "Primary Qualifier Type Code": match["Primary Qualifier Type Code"].replace("B", "Business").replace("O", "Operational").replace("S", "Subject")
            })
        else:
            no_match_records.append(row)

    pqcw_df = pd.DataFrame(records)
    no_match_review = pd.DataFrame(no_match_records)

    return pqcw_df, no_match_review

def find_class_words(df, class_words):
    def find_class_word(name):
        last_word = name.split()[-1]
        match = class_words[class_words["ClassWords"] == last_word]
        return match.iloc[0] if not match.empty else None

    class_word_records = []

    for _, row in df.iterrows():
        match = find_class_word(row["Name"])

        if match is not None:
            row["ClassWords"] = match["ClassWords"]
            row["DataType List"] = match["DataType List"]

        class_word_records.append(row)

    return pd.DataFrame(class_word_records)

def extract_secondary_qualifiers(pqcw_df):
    def remove_primary_and_class_words(name, primary_qualifier, class_words):
        words = name.replace(primary_qualifier, "").replace(class_words, "").strip().split()
        return " ".join(words)

    pqcw_df["Secondary Qualifier"] = pqcw_df.apply(lambda row: remove_primary_and_class_words(row["Name"], row["Primary Qualifier"], row["ClassWords"]), axis=1)
    return pqcw_df

def save_output_to_excel(pqcw_df, no_match_review, output_file):
    with pd.ExcelWriter(output_file) as writer:
        pqcw_df.to_excel(writer, sheet_name="PQCW", index=False)
        no_match_review.to_excel(writer, sheet_name="NoMatchReview", index=False)

def generate_summary_report(pqcw_df, no_match_review):
    primary_qualifier_counts = pqcw_df["Primary Qualifier"].value_counts()
    class_words_counts = pqcw_df["ClassWords"].value_counts()
    combined_counts = pqcw_df.groupby(["Primary Qualifier", "ClassWords"]).size()
    secondary_qualifier_counts = pqcw_df["Secondary Qualifier"].value_counts()
    secondary_qualifier_duplicates = secondary_qualifier_counts[secondary_qualifier_counts > 1]

    report = "Primary Qualifier Counts:\n"
    report += primary_qualifier_counts.to_string() + "\n\n"
    report += "ClassWords Counts:\n"
    report += class_words_counts.to_string() + "\n\n"
    report += "Primary Qualifier + ClassWords Counts:\n"
    report += combined_counts.to_string() + "\n\n"
    report += "Secondary Qualifier Duplicates:\n"
    report += secondary_qualifier_duplicates.to_string()

    return report

def main():
    # Read input files

import pandas as pd
import os

# (Other existing functions)

def find_primary_qualifiers(consolidated_edg, primary_qualifiers):
    # Your implementation here

def find_class_words(df, class_words):
    # Your implementation here

def extract_secondary_qualifiers(pqcw_df):
    # Your implementation here

def save_output_to_excel(pqcw_df, no_match_review, output_file):
    # Your implementation here

def generate_summary_report(pqcw_df, no_match_review):
    # Your implementation here

def main():
    # Read input files
    consolidated_edg = consolidate_edg()
    primary_qualifiers = pd.read_excel("Primary Qualifiers and Class Words.xlsx", sheet_name="Primary Qualifiers")
    class_words = pd.read_excel("Primary Qualifiers and Class Words.xlsx", sheet_name="Class Words")

    # Process data
    pqcw_df, no_match_review = find_primary_qualifiers(consolidated_edg, primary_qualifiers)
    pqcw_df = find_class_words(pqcw_df, class_words)
    no_match_review = find_class_words(no_match_review, class_words)
    pqcw_df = extract_secondary_qualifiers(pqcw_df)

    # Save output to Excel file
    output_file = "PQCW_and_NoMatchReview.xlsx"
    save_output_to_excel(pqcw_df, no_match_review, output_file)

    # Generate summary report
    report = generate_summary_report(pqcw_df, no_match_review)
    print(report)

# Call the main function
if __name__ == "__main__":
    main()
