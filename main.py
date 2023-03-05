import pandas as pd
from fuzzywuzzy import fuzz
from itertools import product


# Load data
edg_df = pd.read_excel('EDG.xlsx')
test_df = pd.read_excel('test.xlsx')
synonyms_df = pd.read_excel('Synonyms.xlsx')


# Define synonym mapping function
def map_synonyms(synonyms_df):
    synonym_dict = {}
    for index, row in synonyms_df.iterrows():
        words = row['Word'].split(",")
        for word in words:
            synonym_dict[word.strip()] = row['Synonyms'].strip()
    return synonym_dict


# Map synonyms
synonym_dict = map_synonyms(synonyms_df)


# Define function to apply synonym mapping
def replace_synonyms(text, synonym_dict):
    words = text.split()
    for i in range(len(words)):
        if words[i] in synonym_dict:
            words[i] = synonym_dict[words[i]]
    return " ".join(words)


# Apply synonym mapping to EDG dataframe
edg_df['Product Name'] = edg_df['Product Name'].apply(lambda x: replace_synonyms(x, synonym_dict))
edg_df['Product Description'] = edg_df['Product Description'].apply(lambda x: replace_synonyms(x, synonym_dict))


# Define function to get top N matches for each query
def get_top_matches(query, choices, limit, min_score=None):
    ratios = []
    for choice in choices:
        ratio = fuzz.token_set_ratio(query, choice)
        if min_score is None or ratio >= min_score:
            ratios.append((choice, ratio))
    ratios = sorted(ratios, key=lambda x: x[1], reverse=True)
    return ratios[:limit]


# Define function to get top N matches for each query in EDG dataframe
def get_top_matches_edg(row, limit):
    name_matches = get_top_matches(row['Product Name'], test_df['Product Name'], limit,35)
    desc_matches = get_top_matches(row['Product Description'], test_df['Product Name'], limit, 35)
    name_df = pd.DataFrame(name_matches, columns=['Name Prediction', 'Name Score'])
    desc_df = pd.DataFrame(desc_matches, columns=['Desc Prediction', 'Desc Score'])
    name_df['ATTRID'] = row['AttributeID']
    name_df['Product Name'] = row['Product Name']
    name_df['Product Description'] = row['Product Description']
    desc_df['ATTRID'] = row['AttributeID']
    desc_df['Product Name'] = row['Product Name']
    desc_df['Product Description'] = row['Product Description']
    return name_df, desc_df


# Get top matches for each row in EDG dataframe
name_dfs = []
desc_dfs = []
for index, row in edg_df.iterrows():
    name_df, desc_df = get_top_matches_edg(row, 5)
    name_dfs.append(name_df)
    desc_dfs.append(desc_df)

# Combine dataframes for each EDG row
name_matches_df = pd.concat(name_dfs, axis=0)
desc_matches_df = pd.concat(desc_dfs, axis=0)

# Output dataframes to separate sheets in output Excel file
with pd.ExcelWriter('output25.xlsx') as writer:
    name_matches_df.to_excel(writer, sheet_name='Name Predictions', index=False)
    desc_matches_df.to_excel(writer, sheet_name='Desc Predictions', index=False)
