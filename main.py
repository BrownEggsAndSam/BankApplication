import pandas as pd

class SynonymProcessor:
    def __init__(self, file_path):
        self.synonym_dict = self.create_synonym_dict(file_path)

    def create_synonym_dict(self, file_path):
        # (existing code for creating synonym dictionary)

    def apply_synonyms(self, df):
        # (existing code for applying synonyms)

########################

import pandas as pd
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

class AttributeProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def get_wordnet_pos(self, word):
        # (existing code for getting wordnet POS)

    def process_files(self, pq_file, cw_file, input_file, synonym_processor):
        # (existing code for processing files, modified to use SynonymProcessor instance)


#############################

import pandas as pd

class AbbreviationProcessor:
    def __init__(self, abbr_file):
        self.abbr_dict = self.create_abbr_dict(abbr_file)

    def create_abbr_dict(self, abbr):
        # (existing code for creating abbreviation dictionary)

    def reformat_attribute_name(self, attribute_name):
        # (existing code for reformatting attribute names)

    def find_occurrences(self, physical_name, occurences):
        # (existing code for finding occurrences)

    def create_output_df(self, input_df, occurences):
        # (existing code for creating output DataFrame)

import pandas as pd

class MainProcessor:
    def __init__(self, attribute_processor, abbreviation_processor):
        self.attribute_processor = attribute_processor
        self.abbreviation_processor = abbreviation_processor

    def process(self, input_df, occurences_file, output_file):
        # (existing code for main processing, modified to use AttributeProcessor and AbbreviationProcessor instances)


from pathlib import Path
from synonym_processor import SynonymProcessor
from attribute_processor import AttributeProcessor
from abbreviation_processor import AbbreviationProcessor
from main_processor import MainProcessor

file_path = './Big_NLP_Tool/Input_Files/'
synonyms_file = file_path + "Synonyms.xlsx"
pq_file = file_path + "PQ.xlsx"
cw_file = file_path + "CW.xlsx"
input_file = file_path + "input.xlsx"
abbr_file = Path(file_path + "Abbreviations.xlsx")
occurences_file = Path(file_path + "Occurences.xlsx")
output_file = Path("./Big_NLP_Tool/Output_Files/pqcwsyn15.xlsx")

synonym_processor = SynonymProcessor(synonyms_file)
attribute_processor = AttributeProcessor()
abbreviation_processor = AbbreviationProcessor(abbr_file)
main_processor = MainProcessor(attribute_processor, abbreviation_processor)

processed_df = attribute_processor.process_files(pq_file, cw_file, input_file, synonym_processor)
main_processor.process(processed_df, occurences_file, output_file)
