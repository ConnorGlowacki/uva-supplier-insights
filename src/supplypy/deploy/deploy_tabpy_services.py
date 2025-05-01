from tabpy.tabpy_tools.client import Client
import pandas as pd
import numpy as np
import click
from rapidfuzz import fuzz
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load data and embeddings
product_data = pd.read_csv("data/TRANSACTIONS.csv", low_memory=False)
embeddings = np.load("outputs/product_desc_embeddings.npy")
model = SentenceTransformer("all-MiniLM-L6-v2")

# HYPERPARAMS
ALPHA = 0.9
BETA = 0.1

# Helper to get similarity scores
def get_similar_items(query, top_n=5, exclude_supplier=None):
    query_embedding = model.encode([query])
    click.echo("Calculating cosine similarity...")
    sims = cosine_similarity(query_embedding, embeddings).flatten()
    df = product_data.copy()
    df["cosine_sim"] = sims
    click.echo("Calculating Levenshtein distance...")
    df['edit_ratio'] = df['Product Description'].apply(lambda x: fuzz.ratio(x, query))

    df["Similarity Score"] = ALPHA * df["cosine_sim"] + BETA * (df["edit_ratio"] / 100.0)

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

def get_pricing_stats_service(query):
        try:
            matches = get_similar_items(query, top_n=20, full=True)
            prices = pd.to_numeric(matches["Unit Price"], errors="coerce").dropna()
            if prices.empty:
                return {}
            return {
                "min": float(prices.min()),
                "25%": float(prices.quantile(0.25)),
                "median": float(prices.median()),
                "75%": float(prices.quantile(0.75)),
                "max": float(prices.max()),
                "mean": float(prices.mean())
            }
        except Exception as e:
            return {"error": str(e)}
 
def get_supplier_summary_service(query):
    try:
        df = get_similar_items(query, top_n=20, full=True)
        if "Supplier Name" not in df.columns:
            return []
        summary = df.groupby("Supplier Name").agg(
            Orders=('Product Description', 'count'),
            Avg_Price=('Unit Price', 'mean')
        ).reset_index()
        return summary.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]

def get_buyer_summary_service(query):
    try:
        df = get_similar_items(query, top_n=20, full=True)
        col = "Original Requisition Requestor"
        if col not in df.columns and "Buyer: First Name" in df.columns and "Buyer: Last Name" in df.columns:
            df["Buyer"] = df["Buyer: First Name"].astype(str) + " " + df["Buyer: Last Name"].astype(str)
            col = "Buyer"
        if col not in df.columns:
            return []
        summary = df.groupby(col).agg(
            Orders=('Product Description', 'count'),
            Avg_Price=('Unit Price', 'mean')
        ).reset_index()
        return summary.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]

def deploy_services(
        host: str, 
        username: str = None, 
        password: str = None
    ):
    # Connect and deploy
    client = Client(host)
    if username and password:
        client.set_credentials(username, password)

    client.deploy('get_top_matches', get_top_matches_service, "Returns top 5 similar products", override=True)
    client.deploy('get_competitors', get_competitors_service, "Returns top 5 competitors", override=True)
    client.deploy('get_cluster_id', get_cluster_id_service, "Returns cluster ID for query", override=True)
    client.deploy('get_pricing_stats', get_pricing_stats_service, "Returns price distribution", override=True)
    client.deploy('get_supplier_summary', get_supplier_summary_service, "Returns aggregated supplier insights", override=True)
    client.deploy('get_buyer_summary', get_buyer_summary_service, "Returns purchasing behavior info", override=True)
 