from tabpy.tabpy_tools.client import Client
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load data and embeddings
product_data = pd.read_csv("data/TRANSACTIONS.csv", low_memory=False)
embeddings = np.load("outputs/product_desc_embeddings.npy")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Helper to get similarity scores
def get_similar_items(query, top_n=5, exclude_supplier=None):
    query_embedding = model.encode([query])
    sims = cosine_similarity(query_embedding, embeddings).flatten()
    df = product_data.copy()
    df["Similarity Score"] = sims

    if exclude_supplier:
        df = df[df["Supplier Name"] != exclude_supplier]

    df = df.sort_values("Similarity Score", ascending=False)
    top = df.head(top_n)

    # Pad if not enough results
    if len(top) < top_n:
        pad_df = pd.DataFrame([{
            "Product Description": "",
            "Supplier Name": "",
            "Unit Price": np.nan,
            "Similarity Score": 0.0
        }] * (top_n - len(top)))
        top = pd.concat([top, pad_df], ignore_index=True)

    return top

# Deployable TabPy functions
def get_top_matches_service(query):
    try:
        results = get_similar_items(query, top_n=5)
        return results.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]

def get_competitors_service(query):
    try:
        top = get_similar_items(query, top_n=1)
        if top.empty or top.iloc[0]["Supplier Name"] == "":
            return []
        main_supplier = top.iloc[0]["Supplier Name"]
        competitors = get_similar_items(top.iloc[0]["Product Description"], top_n=5, exclude_supplier=main_supplier)
        return competitors.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]

def get_cluster_id_service(query):
    try:
        query_embedding = model.encode([query])
        sims = cosine_similarity(query_embedding, embeddings).flatten()
        idx = sims.argmax()
        return int(product_data.iloc[idx]["Cluster"])
    except Exception as e:
        return -1  # Default to -1 for error

def deploy_services():
    # Connect and deploy
    client = Client("http://localhost:9004/")
    client.deploy('get_top_matches', get_top_matches_service, "Returns top 5 similar products", override=True)
    client.deploy('get_competitors', get_competitors_service, "Returns top 5 competitors", override=True)
    client.deploy('get_cluster_id', get_cluster_id_service, "Returns cluster ID for query", override=True)