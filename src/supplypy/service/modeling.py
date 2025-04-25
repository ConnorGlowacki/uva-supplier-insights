import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Loading clustered product data and embeddings
product_data = pd.read_csv("outputs/TRANSACTIONS.csv")
embeddings = np.load("outputs/product_desc_embeddings.npy")

# Loading embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_top_matches(query, top_n=5):
    query_embedding = model.encode([query])
    sims = cosine_similarity(query_embedding, embeddings).flatten()
    top_indices = sims.argsort()[-top_n:][::-1]
    df = product_data.iloc[top_indices].copy()
    df["Similarity Score"] = sims[top_indices]
    return df.to_dict(orient="records")

def find_competitive_alternatives(query, top_n=5):
    top = get_top_matches(query, top_n=1)
    if not top:
        return []
    top_supplier = top[0]['Supplier Name']
    query_embedding = model.encode([top[0]['Product Description']])
    sims = cosine_similarity(query_embedding.reshape(1, -1), embeddings).flatten()
    product_data["Similarity Score"] = sims
    df = product_data[product_data["Supplier Name"] != top_supplier]
    df = df.sort_values("Similarity Score", ascending=False).head(top_n)
    return df.to_dict(orient="records")

def get_cluster_for_query(query):
    query_embedding = model.encode([query])
    sims = cosine_similarity(query_embedding, embeddings).flatten()
    idx = sims.argmax()
    return int(product_data.iloc[idx]["Cluster"])