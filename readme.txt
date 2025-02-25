import pandas as pd
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from rapidfuzz import fuzz, process
from gensim.models import KeyedVectors
from scipy.spatial.distance import euclidean

# Load pre-trained Word2Vec model (optional for WMD)
# model = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary=True)

def load_data(edg_file, request_file):
    print("Loading Excel files...")
    edg = pd.read_excel(edg_file)
    request = pd.read_excel(request_file)
    print("Files loaded successfully.")
    return edg, request

def compute_tfidf_similarity(edg_defs, request_defs):
    print("Computing TF-IDF Cosine Similarity...")
    start_time = time.time()
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(edg_defs + request_defs)
    edg_tfidf = tfidf_matrix[:len(edg_defs)]
    request_tfidf = tfidf_matrix[len(edg_defs):]
    similarity_matrix = cosine_similarity(request_tfidf, edg_tfidf)
    print(f"TF-IDF Computation Time: {time.time() - start_time:.2f} seconds")
    return similarity_matrix

def compute_bert_similarity(edg_defs, request_defs):
    print("Computing BERT Embedding Similarity...")
    start_time = time.time()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    edg_embeddings = model.encode(edg_defs, convert_to_tensor=True)
    request_embeddings = model.encode(request_defs, convert_to_tensor=True)
    similarity_matrix = cosine_similarity(request_embeddings.cpu(), edg_embeddings.cpu())
    print(f"BERT Computation Time: {time.time() - start_time:.2f} seconds")
    return similarity_matrix

def compute_jaccard_similarity(edg_defs, request_defs):
    print("Computing Jaccard Similarity...")
    start_time = time.time()
    def jaccard(str1, str2):
        set1, set2 = set(str1.split()), set(str2.split())
        return len(set1 & set2) / len(set1 | set2)
    
    similarity_matrix = np.zeros((len(request_defs), len(edg_defs)))
    for i, r_def in tqdm(enumerate(request_defs), total=len(request_defs)):
        for j, e_def in enumerate(edg_defs):
            similarity_matrix[i, j] = jaccard(r_def, e_def)
    print(f"Jaccard Computation Time: {time.time() - start_time:.2f} seconds")
    return similarity_matrix

def compute_levenshtein_similarity(edg_defs, request_defs):
    print("Computing Levenshtein Similarity...")
    start_time = time.time()
    similarity_matrix = np.zeros((len(request_defs), len(edg_defs)))
    for i, r_def in tqdm(enumerate(request_defs), total=len(request_defs)):
        for j, e_def in enumerate(edg_defs):
            similarity_matrix[i, j] = fuzz.ratio(r_def, e_def) / 100
    print(f"Levenshtein Computation Time: {time.time() - start_time:.2f} seconds")
    return similarity_matrix

def generate_output(similarity_matrix, request_df, edg_df, method, writer):
    threshold = 0.7
    results = []
    print(f"Processing {method} results...")
    for i, row in enumerate(similarity_matrix):
        matches = sorted(enumerate(row), key=lambda x: x[1], reverse=True)
        for idx, score in matches:
            if score >= threshold:
                results.append([
                    request_df.iloc[i]['Attribute ID'], request_df.iloc[i]['Definition'],
                    edg_df.iloc[idx]['Attribute ID'], edg_df.iloc[idx]['Attribute Definition'],
                    score
                ])
    
    df_results = pd.DataFrame(results, columns=['Request Attribute ID', 'Request Definition',
                                                'Matched Attribute ID', 'Matched Definition',
                                                'Similarity Score'])
    df_results.sort_values(by='Similarity Score', ascending=False, inplace=True)
    df_results.to_excel(writer, sheet_name=method, index=False)
    print(f"{method} results saved.")

def main():
    edg_file = input("Enter path to EDG file: ")
    request_file = input("Enter path to Request Document: ")
    output_file = "Similarity_Results.xlsx"
    
    edg_df, request_df = load_data(edg_file, request_file)
    edg_defs = edg_df['Attribute Definition'].fillna("").tolist()
    request_defs = request_df['Definition'].fillna("").tolist()
    
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    
    similarity_methods = {
        'TF-IDF': compute_tfidf_similarity,
        'BERT': compute_bert_similarity,
        'Jaccard': compute_jaccard_similarity,
        'Levenshtein': compute_levenshtein_similarity
    }
    
    for method, func in similarity_methods.items():
        sim_matrix = func(edg_defs, request_defs)
        generate_output(sim_matrix, request_df, edg_df, method, writer)
    
    writer.close()
    print(f"Results saved in {output_file}")

if __name__ == "__main__":
    main()
