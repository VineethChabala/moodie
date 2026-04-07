import os
import gdown
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import streamlit as st

class SemanticRecommender():
    def __init__(self):
        try:
            hf_token = st.secrets["HUGGINGFACE_API_KEY"]
            csv_drive_id = st.secrets["CSV_DRIVE_ID"]
            npy_drive_id = st.secrets["NPY_DRIVE_ID"]
        except (FileNotFoundError, KeyError):
            st.error("HuggingFace API Key not found. Please set it in secrets.")
            hf_token = None
            
        self.model_client = SentenceTransformer('all-MiniLM-L6-v2', token=hf_token)
        
        # --- DYNAMIC DOWNLOAD LOGIC ---
        csv_file = 'cleaned_movies.csv'
        npy_file = 'movie_embeddings.npy'
        
        # Replace these with your actual Google Drive file IDs
        # To get the ID: right-click file -> Share -> Copy link
        # The ID is the long string of letters and numbers between /d/ and /view
        
        if not os.path.exists(csv_file):
            st.info(f"Downloading {csv_file} from Google Drive...")
            try:
                gdown.download(id=csv_drive_id, output=csv_file, quiet=False)
            except Exception as e:
                st.error(f"Failed to download CSV: {e}")
                
        if not os.path.exists(npy_file):
            st.info(f"Downloading {npy_file} from Google Drive...")
            try:
                gdown.download(id=npy_drive_id, output=npy_file, quiet=False)
            except Exception as e:
                st.error(f"Failed to download NPY: {e}")

        # Load the files
        self.df = pd.read_csv(csv_file)
        self.embedding = np.load(npy_file)

    def get_recommendations(self, prompt, top_k=10):
        query_embedding = self.model_client.encode([prompt])
        # semantic_search returns a list of lists of dicts: [[{'corpus_id': int, 'score': float}, ...]]
        # It also automatically sorts by score descending, so we don't need argsort!
        results = util.semantic_search(query_embedding, self.embedding, top_k=top_k)[0]
        
        # Extract the corpus_id to use as row indices for our DataFrame
        top_indices = [hit["corpus_id"] for hit in results]
        return self.df.iloc[top_indices]


if __name__ == "__main__":
    recommender = SemanticRecommender()
    print(recommender.get_recommendations("Comedy movie with police officers"))
