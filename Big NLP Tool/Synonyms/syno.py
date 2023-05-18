import pandas as pd

## Will take a list of words and update them into a dictionary of synonyms.

def add_synonyms(synonyms, word, synonym):
    if word not in synonyms:
        synonyms[word] = set()

    if synonym not in synonyms:
        synonyms[synonym] = set()

    synonyms[word].add(synonym)
    synonyms[synonym].add(word)

def create_synonym_dict(file_path):
    df = pd.read_excel(file_path)

    synonyms = {}
    for _, row in df.iterrows():
        word, synonym = row['Word'], row['Synonym']
        add_synonyms(synonyms, word, synonym)

    # Propagate synonyms of synonyms
    updated = True
    while updated:
        updated = False
        for word in synonyms:
            current_synonyms = list(synonyms[word])
            for synonym in current_synonyms:
                new_synonyms = synonyms[synonym] - synonyms[word] - {word}
                if new_synonyms:
                    updated = True
                    synonyms[word].update(new_synonyms)

    # Convert sets to lists and sort
    for word in synonyms:
        synonyms[word] = sorted(list(synonyms[word]))

    return synonyms

file_path = './Big NLP Tool/Synonyms/Synonyms.xlsx'
synonym_dict = create_synonym_dict(file_path)
print(synonym_dict)