import pandas as pd
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from rapidfuzz import fuzz
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os

# Define file paths
package_input_path = './__rationalizationTool/input/'
package_output_path = './__rationalizationTool/output/'
edgDataDictionary = package_input_path + 'EDG.xlsx'
requestFile = package_input_path + 'Request.xlsx'
output_file = package_output_path + 'Results.xlsx'

# Ensure output directory exists
os.makedirs(package_output_path, exist_ok=True)

# Try to initialize NLTK resources locally
try:
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
except LookupError:
    # If NLTK resources aren't available, use a basic stopword list
    print("NLTK resources not found. Using basic stopword list.")
    stop_words = {"a", "an", "the", "and", "or", "but", "if", "because", "as", "what", 
                "which", "this", "that", "these", "those", "then", "just", "so", "than", "such",
                "for", "is", "in", "to", "of", "at", "by", "with", "about", "not"}
    
    # Simple lemmatizer function as fallback
    def simple_lemmatize(word):
        # Very basic lemmatization rules
        if word.endswith('s') and not word.endswith(('ss', 'us', 'is')):
            return word[:-1]
        if word.endswith('es'):
            return word[:-2]
        if word.endswith('ed') and len(word) > 4:
            return word[:-2]
        if word.endswith('ing') and len(word) > 5:
            return word[:-3]
        return word
    
    # Create a simple lemmatizer class with a lemmatize method
    class SimpleLemmatizer:
        def lemmatize(self, word, pos=None):
            return simple_lemmatize(word)
    
    lemmatizer = SimpleLemmatizer()

def preprocess_text(text):
    """Preprocess text by removing special characters, lemmatizing, and removing stopwords"""
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Tokenize and lemmatize
    words = text.split()
    filtered_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    
    return ' '.join(filtered_words)

def load_data(edg_file, request_file):
    print("Loading Excel files...")
    try:
        edg = pd.read_excel(edg_file)
        request = pd.read_excel(request_file)
        print("Files loaded successfully.")
        
        # Verify required columns exist
        if 'Attribute Definition' not in edg.columns:
            print(f"Warning: 'Attribute Definition' column not found in EDG file. Available columns: {edg.columns.tolist()}")
        
        if 'Definition' not in request.columns:
            print(f"Warning: 'Definition' column not found in Request file. Available columns: {request.columns.tolist()}")
            
        return edg, request
    except Exception as e:
        print(f"Error loading files: {e}")
        return None, None

def compute_tfidf_similarity(edg_defs, request_defs):
    print("Computing TF-IDF Cosine Similarity...")
    start_time = time.time()
    
    # Create TF-IDF vectorizer with n-grams
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.95)
    
    # Handle empty inputs
    if not edg_defs or not request_defs:
        print("Warning: Empty definition lists provided")
        return np.zeros((len(request_defs), len(edg_defs)))
    
    # Fit and transform
    tfidf_matrix = vectorizer.fit_transform(edg_defs + request_defs)
    edg_tfidf = tfidf_matrix[:len(edg_defs)]
    request_tfidf = tfidf_matrix[len(edg_defs):]
    
    # Calculate similarity in batches to avoid memory issues
    batch_size = 100
    num_batches = (len(request_defs) + batch_size - 1) // batch_size
    similarity_matrix = np.zeros((len(request_defs), len(edg_defs)))
    
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(request_defs))
        batch_similarity = cosine_similarity(request_tfidf[start_idx:end_idx], edg_tfidf)
        similarity_matrix[start_idx:end_idx] = batch_similarity
    
    print(f"TF-IDF Computation Time: {time.time() - start_time:.2f} seconds")
    return similarity_matrix

def compute_weighted_similarity(edg_defs, request_defs, edg_df, request_df):
    print("Computing Weighted Similarity (TF-IDF + Fuzzy)...")
    start_time = time.time()
    
    # Get TF-IDF similarity
    tfidf_matrix = compute_tfidf_similarity(edg_defs, request_defs)
    
    # Compute fuzzy matching for each pair (in batches to manage memory)
    print("Computing Fuzzy Similarity...")
    fuzzy_matrix = np.zeros((len(request_defs), len(edg_defs)))
    batch_size = 50
    
    for i in tqdm(range(0, len(request_defs), batch_size)):
        batch_end = min(i + batch_size, len(request_defs))
        for j in range(i, batch_end):
            if not isinstance(request_defs[j], str) or not request_defs[j].strip():
                continue
                
            for k in range(len(edg_defs)):
                if not isinstance(edg_defs[k], str) or not edg_defs[k].strip():
                    continue
                    
                # Use token_sort_ratio for better handling of word order differences
                fuzzy_matrix[j, k] = fuzz.token_sort_ratio(request_defs[j], edg_defs[k]) / 100
    
    # Combine scores (70% TF-IDF, 30% fuzzy)
    combined_matrix = (0.7 * tfidf_matrix) + (0.3 * fuzzy_matrix)
    
    print(f"Weighted Similarity Computation Time: {time.time() - start_time:.2f} seconds")
    return combined_matrix

def compute_jaccard_similarity(edg_defs, request_defs):
    print("Computing Jaccard Similarity...")
    start_time = time.time()
    
    def jaccard(str1, str2):
        if not isinstance(str1, str) or not isinstance(str2, str):
            return 0
        set1, set2 = set(str1.split()), set(str2.split())
        if not set1 or not set2:
            return 0
        return len(set1 & set2) / len(set1 | set2)
    
    similarity_matrix = np.zeros((len(request_defs), len(edg_defs)))
    batch_size = 50
    
    for i in tqdm(range(0, len(request_defs), batch_size)):
        batch_end = min(i + batch_size, len(request_defs))
        for j in range(i, batch_end):
            for k in range(len(edg_defs)):
                similarity_matrix[j, k] = jaccard(request_defs[j], edg_defs[k])
    
    print(f"Jaccard Computation Time: {time.time() - start_time:.2f} seconds")
    return similarity_matrix

def compute_fuzzy_similarity(edg_defs, request_defs):
    print("Computing Fuzzy Match Similarity...")
    start_time = time.time()
    
    similarity_matrix = np.zeros((len(request_defs), len(edg_defs)))
    batch_size = 50
    
    for i in tqdm(range(0, len(request_defs), batch_size)):
        batch_end = min(i + batch_size, len(request_defs))
        for j in range(i, batch_end):
            if not isinstance(request_defs[j], str) or not request_defs[j].strip():
                continue
                
            for k in range(len(edg_defs)):
                if not isinstance(edg_defs[k], str) or not edg_defs[k].strip():
                    continue
                    
                # Use token_sort_ratio for better handling of word order differences
                similarity_matrix[j, k] = fuzz.token_sort_ratio(request_defs[j], edg_defs[k]) / 100
    
    print(f"Fuzzy Match Computation Time: {time.time() - start_time:.2f} seconds")
    return similarity_matrix

def generate_output(similarity_matrix, request_df, edg_df, method, writer):
    threshold = 0.7
    results = []
    print(f"Processing {method} results...")
    
    for i, row in enumerate(similarity_matrix):
        if i >= len(request_df):
            print(f"Warning: Index {i} exceeds request dataframe length {len(request_df)}")
            continue
            
        # Get top matches above threshold
        matches = sorted(enumerate(row), key=lambda x: x[1], reverse=True)
        
        request_id = request_df.iloc[i].get('Attribute ID', 'Unknown')
        request_def = request_df.iloc[i].get('Definition', '')
        
        matches_added = 0
        for idx, score in matches:
            if score >= threshold and idx < len(edg_df):
                matched_id = edg_df.iloc[idx].get('Attribute ID', 'Unknown')
                matched_def = edg_df.iloc[idx].get('Attribute Definition', '')
                
                results.append([
                    request_id, request_def,
                    matched_id, matched_def,
                    score
                ])
                matches_added += 1
                
                # Limit to top 10 matches per request item to keep output manageable
                if matches_added >= 10:
                    break
    
    # Create DataFrame and save to Excel
    if results:
        df_results = pd.DataFrame(results, columns=['Request Attribute ID', 'Request Definition',
                                                   'Matched Attribute ID', 'Matched Definition',
                                                   'Similarity Score'])
        df_results.sort_values(by=['Request Attribute ID', 'Similarity Score'], 
                             ascending=[True, False], inplace=True)
        df_results.to_excel(writer, sheet_name=method, index=False)
        print(f"{method} results saved with {len(df_results)} matches.")
    else:
        # Create empty dataframe if no results
        pd.DataFrame(columns=['Request Attribute ID', 'Request Definition',
                            'Matched Attribute ID', 'Matched Definition',
                            'Similarity Score']).to_excel(writer, sheet_name=method, index=False)
        print(f"No matches found for {method} with threshold {threshold}.")

def main():
    # Load data
    edg_df, request_df = load_data(edgDataDictionary, requestFile)
    if edg_df is None or request_df is None:
        print("Error: Failed to load data. Exiting.")
        return
    
    # Preprocess text data
    print("Preprocessing definitions...")
    edg_defs = [preprocess_text(text) for text in edg_df['Attribute Definition'].fillna("").tolist()]
    request_defs = [preprocess_text(text) for text in request_df['Definition'].fillna("").tolist()]
    
    # Create Excel writer
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Define similarity methods to use
            similarity_methods = {
                'TF-IDF': compute_tfidf_similarity,
                'Fuzzy': compute_fuzzy_similarity,
                'Jaccard': compute_jaccard_similarity,
                'Weighted': lambda e, r: compute_weighted_similarity(e, r, edg_df, request_df)
            }
            
            # Generate results for each method
            for method, func in similarity_methods.items():
                print(f"\nRunning {method} similarity...")
                sim_matrix = func(edg_defs, request_defs)
                generate_output(sim_matrix, request_df, edg_df, method, writer)
            
            # Add a summary sheet
            print("Creating summary sheet...")
            pd.DataFrame({
                'Method': list(similarity_methods.keys()),
                'Description': [
                    'TF-IDF vector similarity with n-grams (1-2)',
                    'Fuzzy string matching (token sort ratio)',
                    'Jaccard similarity of word sets',
                    'Combined weighted score (70% TF-IDF, 30% Fuzzy)'
                ]
            }).to_excel(writer, sheet_name='Methods', index=False)
                
        print(f"Results saved in {output_file}")
    except Exception as e:
        print(f"Error writing results: {e}")

if __name__ == "__main__":
    main()
