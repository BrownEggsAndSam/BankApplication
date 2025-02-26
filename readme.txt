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
from collections import Counter

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

def extract_technical_terms(text):
    """Extract likely technical terms from text based on patterns and frequency"""
    if not isinstance(text, str):
        return []
        
    # Remove punctuation and convert to lowercase
    cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Split into words
    words = cleaned_text.split()
    
    # Find potential technical terms (uppercase words, words with underscores, camelCase, etc.)
    technical_terms = []
    
    # Extract potential camelCase or PascalCase words
    camel_case_pattern = re.compile(r'([a-z])([A-Z])')
    
    for word in words:
        # Words with specific patterns that suggest they are technical terms
        if (any(c.isupper() for c in word) or 
            '_' in word or 
            (len(word) >= 4 and word not in stop_words) or
            bool(camel_case_pattern.search(word))):
            technical_terms.append(word)
    
    return technical_terms

def preprocess_text(text, extract_terms=False):
    """Preprocess text by removing special characters, lemmatizing, and removing stopwords"""
    if not isinstance(text, str):
        return ""
    
    # Extract technical terms before preprocessing if requested
    technical_terms = extract_technical_terms(text) if extract_terms else []
    
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Tokenize and lemmatize
    words = text.split()
    filtered_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    
    # Add technical terms back (to preserve their importance)
    if technical_terms:
        filtered_words.extend(technical_terms)
    
    return ' '.join(filtered_words)

def load_data(edg_file, request_file):
    print("Loading Excel files...")
    try:
        edg = pd.read_excel(edg_file)
        request = pd.read_excel(request_file)
        print("Files loaded successfully.")
        
        # Verify required columns exist
        edg_cols = edg.columns.tolist()
        req_cols = request.columns.tolist()
        
        if 'Attribute Definition' not in edg_cols:
            print(f"Warning: 'Attribute Definition' column not found in EDG file. Available columns: {edg_cols}")
        
        if 'Definition' not in req_cols:
            print(f"Warning: 'Definition' column not found in Request file. Available columns: {req_cols}")
            
        if 'Logical Name' not in req_cols:
            print(f"Warning: 'Logical Name' column not found in Request file.")
            
        if 'Physical Name' not in req_cols:
            print(f"Warning: 'Physical Name' column not found in Request file.")
            
        return edg, request
    except Exception as e:
        print(f"Error loading files: {e}")
        return None, None

def compute_tfidf_similarity(edg_defs, request_defs):
    print("Computing TF-IDF Cosine Similarity...")
    start_time = time.time()
    
    # Create TF-IDF vectorizer with n-grams
    vectorizer = TfidfVectorizer(ngram_range=(1, 3), min_df=1, max_df=0.95)
    
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

def compute_enhanced_similarity(edg_defs, request_defs, edg_names, request_names_logical, request_names_physical):
    """Compute similarity with multiple factors including names"""
    print("Computing Enhanced Similarity (definitions + names)...")
    start_time = time.time()
    
    # 1. Get TF-IDF similarity for definitions
    print("Computing definition similarity...")
    def_similarity = compute_tfidf_similarity(edg_defs, request_defs)
    
    # 2. Calculate name similarity using fuzzy matching
    print("Computing name similarity...")
    name_similarity = np.zeros((len(request_defs), len(edg_defs)))
    
    for i in tqdm(range(len(request_names_logical))):
        logical_name = str(request_names_logical[i]) if not pd.isna(request_names_logical[i]) else ""
        physical_name = str(request_names_physical[i]) if not pd.isna(request_names_physical[i]) else ""
        
        for j in range(len(edg_names)):
            edg_name = str(edg_names[j]) if not pd.isna(edg_names[j]) else ""
            
            # Compare logical name to EDG name
            logical_score = fuzz.token_set_ratio(logical_name, edg_name) / 100 if logical_name else 0
            
            # Compare physical name to EDG name
            physical_score = fuzz.token_set_ratio(physical_name, edg_name) / 100 if physical_name else 0
            
            # Take the best match between logical and physical
            name_similarity[i, j] = max(logical_score, physical_score)
    
    # 3. Compute key terms overlap
    print("Computing key terms overlap...")
    term_similarity = np.zeros((len(request_defs), len(edg_defs)))
    
    # Extract and count key terms from all definitions
    edg_terms = [extract_technical_terms(text) for text in edg_defs]
    request_terms = [extract_technical_terms(text) for text in request_defs]
    
    for i in range(len(request_terms)):
        req_terms = set(request_terms[i])
        if not req_terms:
            continue
            
        for j in range(len(edg_terms)):
            edg_term_set = set(edg_terms[j])
            if not edg_term_set:
                continue
                
            # Calculate Jaccard similarity of technical terms
            intersection = len(req_terms.intersection(edg_term_set))
            union = len(req_terms.union(edg_term_set))
            term_similarity[i, j] = intersection / union if union > 0 else 0
    
    # Combine the similarities with weights
    # 60% definition, 25% name, 15% term overlap
    combined_similarity = (0.6 * def_similarity) + (0.25 * name_similarity) + (0.15 * term_similarity)
    
    print(f"Enhanced Similarity Computation Time: {time.time() - start_time:.2f} seconds")
    return combined_similarity

def compute_context_aware_similarity(edg_defs, request_defs, edg_df, request_df):
    """Compute similarity with contextual weighting based on content analysis"""
    print("Computing Context-Aware Similarity...")
    start_time = time.time()
    
    # 1. Analyze definition types (technical, descriptive, etc.)
    def analyze_text_type(text):
        if not isinstance(text, str) or not text.strip():
            return "empty"
            
        # Count different types of content
        technical_count = len(re.findall(r'\b(?:id|key|code|data|field|table|column|value|type|format)\b', text.lower()))
        descriptive_count = len(re.findall(r'\b(?:describes|represents|indicates|shows|contains|includes|provides)\b', text.lower()))
        
        # Detect if it's a technical definition or more descriptive
        if technical_count > descriptive_count:
            return "technical"
        else:
            return "descriptive"
    
    request_types = [analyze_text_type(text) for text in request_defs]
    edg_types = [analyze_text_type(text) for text in edg_defs]
    
    # 2. Base TF-IDF similarity
    tfidf_similarity = compute_tfidf_similarity(edg_defs, request_defs)
    
    # 3. Compute fuzzy token sort ratio
    fuzzy_similarity = np.zeros((len(request_defs), len(edg_defs)))
    for i in tqdm(range(len(request_defs))):
        if not isinstance(request_defs[i], str) or not request_defs[i].strip():
            continue
            
        for j in range(len(edg_defs)):
            if not isinstance(edg_defs[j], str) or not edg_defs[j].strip():
                continue
                
            fuzzy_similarity[i, j] = fuzz.token_sort_ratio(request_defs[i], edg_defs[j]) / 100
    
    # 4. Adjust weights based on definition types
    context_aware_similarity = np.zeros((len(request_defs), len(edg_defs)))
    
    for i in range(len(request_defs)):
        for j in range(len(edg_defs)):
            # Default weights
            tfidf_weight = 0.7
            fuzzy_weight = 0.3
            
            # Adjust weights based on text types
            if request_types[i] == "technical" and edg_types[j] == "technical":
                # For technical definitions, exact matches are more important
                tfidf_weight = 0.8
                fuzzy_weight = 0.2
            elif request_types[i] == "descriptive" and edg_types[j] == "descriptive":
                # For descriptive text, fuzzy matching is more important
                tfidf_weight = 0.6
                fuzzy_weight = 0.4
            
            # Combine with adjusted weights
            context_aware_similarity[i, j] = (tfidf_weight * tfidf_similarity[i, j]) + (fuzzy_weight * fuzzy_similarity[i, j])
    
    print(f"Context-Aware Similarity Computation Time: {time.time() - start_time:.2f} seconds")
    return context_aware_similarity

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
                    
                # Use token_set_ratio for better handling of different lengths and word order
                similarity_matrix[j, k] = fuzz.token_set_ratio(request_defs[j], edg_defs[k]) / 100
    
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
        
        # Get Logical and Physical names
        logical_name = request_df.iloc[i].get('Logical Name', '')
        physical_name = request_df.iloc[i].get('Physical Name', '')
        
        matches_added = 0
        for idx, score in matches:
            if score >= threshold and idx < len(edg_df):
                matched_id = edg_df.iloc[idx].get('Attribute ID', 'Unknown')
                matched_def = edg_df.iloc[idx].get('Attribute Definition', '')
                matched_name = edg_df.iloc[idx].get('Attribute Name', '')
                
                results.append([
                    request_id, logical_name, physical_name, request_def,
                    matched_id, matched_name, matched_def,
                    score
                ])
                matches_added += 1
                
                # Limit to top 10 matches per request item to keep output manageable
                if matches_added >= 10:
                    break
    
    # Create DataFrame and save to Excel
    if results:
        df_results = pd.DataFrame(results, columns=[
            'Request Attribute ID', 'Logical Name', 'Physical Name', 'Request Definition',
            'Matched Attribute ID', 'Matched Attribute Name', 'Matched Definition',
            'Similarity Score'
        ])
        df_results.sort_values(by=['Request Attribute ID', 'Similarity Score'], 
                             ascending=[True, False], inplace=True)
        
        # Apply conditional formatting
        workbook = writer.book
        worksheet = writer.sheets[method]
        
        # Add number format for similarity score
        format_percent = workbook.add_format({'num_format': '0.00%'})
        
        # Convert similarity score to Excel percentage format
        df_results['Similarity Score'] = df_results['Similarity Score'].astype(float)
        
        # Write the DataFrame to Excel
        df_results.to_excel(writer, sheet_name=method, index=False)
        
        # Set column widths
        for i, col in enumerate(df_results.columns):
            max_len = max(df_results[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(max_len, 50))
        
        # Apply conditional formatting to similarity score column
        score_col = df_results.columns.get_loc('Similarity Score')
        worksheet.conditional_format(1, score_col, len(df_results) + 1, score_col, {
            'type': '3_color_scale',
            'min_color': '#FFFFFF',
            'mid_color': '#AED6F1',
            'max_color': '#2E86C1'
        })
        
        print(f"{method} results saved with {len(df_results)} matches.")
    else:
        # Create empty dataframe if no results
        pd.DataFrame(columns=[
            'Request Attribute ID', 'Logical Name', 'Physical Name', 'Request Definition',
            'Matched Attribute ID', 'Matched Attribute Name', 'Matched Definition',
            'Similarity Score'
        ]).to_excel(writer, sheet_name=method, index=False)
        print(f"No matches found for {method} with threshold {threshold}.")

def main():
    # Load data
    edg_df, request_df = load_data(edgDataDictionary, requestFile)
    if edg_df is None or request_df is None:
        print("Error: Failed to load data. Exiting.")
        return
    
    # Preprocess text data
    print("Preprocessing definitions...")
    edg_defs = [preprocess_text(text, extract_terms=True) for text in edg_df['Attribute Definition'].fillna("").tolist()]
    request_defs = [preprocess_text(text, extract_terms=True) for text in request_df['Definition'].fillna("").tolist()]
    
    # Get name columns for enhanced matching
    edg_names = edg_df['Attribute Name'].fillna("").tolist()
    request_logical_names = request_df['Logical Name'].fillna("").tolist()
    request_physical_names = request_df['Physical Name'].fillna("").tolist()
    
    # Create Excel writer
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Define similarity methods to use
            similarity_methods = {
                'Enhanced': lambda e, r: compute_enhanced_similarity(e, r, edg_names, request_logical_names, request_physical_names),
                'Context-Aware': lambda e, r: compute_context_aware_similarity(e, r, edg_df, request_df),
                'TF-IDF': compute_tfidf_similarity,
                'Fuzzy': compute_fuzzy_similarity,
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
                    'Enhanced similarity combining definitions, names, and technical terms (Recommended)',
                    'Context-aware matching that adjusts weights based on definition types',
                    'TF-IDF vector similarity with n-grams (1-3)',
                    'Fuzzy string matching (token set ratio)',
                    'Combined weighted score (70% TF-IDF, 30% Fuzzy)'
                ],
                'Best For': [
                    'Overall best performance balancing all factors',
                    'Mixed content with varying styles of definitions',
                    'Detailed technical definitions with specific terminology',
                    'Short descriptions or when word order varies',
                    'General purpose matching'
                ]
            }).to_excel(writer, sheet_name='Methods', index=False)
                
        print(f"Results saved in {output_file}")
    except Exception as e:
        print(f"Error writing results: {e}")

if __name__ == "__main__":
    main()
