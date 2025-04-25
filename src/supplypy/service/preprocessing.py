import os
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm
import click
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

DATA_DIR = "data"
OUTPUT_DIR = "outputs"
TRANSACTION_DIR = os.path.join(DATA_DIR, "transactions")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRANSACTION_DIR, exist_ok=True)


DOC_DF_PATH = os.path.join(DATA_DIR, "DOC.csv")
TRANSATIONS_PATH = os.path.join(DATA_DIR, "TRANSACTIONS.csv")
EMBEDDINGS_PATH = os.path.join(OUTPUT_DIR, "product_desc_embeddings.npy")

PAYMENTS_HDR = [
    "PO ID",
    "Creation Date",
    "Original Revision Date",
    "Last Revision Date",
    "Last Distribution Date",
    "Workflow Completion Date",
    "PO #",
    "Requested Deliver Date",
    "PR ID",
    "Payment Type",
    "PO Terms",
    "Buyer: First Name",
    "Buyer: Last Name",
    "Buyer Phone",
    "Buyer: Email",
    "Department",
    "Supplier Fax",
    "BillTo Address Code",
    "BillTo Address Internal Name",
    "BillTo Contact 1",
    "BillTo Address 1",
    "BillTo City",
    "BillTo State",
    "BillTo Postal Code",
    "BillTo Country",
    "Accounting Date",
    "ShipTo Address Code",
    "ShipTo Address Internal Name",
    "ShipTo Contact 1",
    "ShipTo Contact 2",
    "ShipTo Contact 3",
    "ShipTo Address 1",
    "ShipTo Address 2",
    "ShipTo City",
    "ShipTo State",
    "ShipTo Postal Code",
    "ShipTo Country",
    "Supplier ID",
    "Customer SupplierId",
    "Supplier Name",
    "Supplier Number",
    "Header Notes",
    "PO Line #",
    "Quantity",
    "Unit Price",
    "Unit Price Date",
    "Extended Price",
    "List Price",
    "List Price Date",
    "Current - 1 Unit Price",
    "Current - 1 Unit Price Date",
    "Current - 1 List Price",
    "Current - 1 List Price Date",
    "Currency",
    "SKU/Catalog #",
    "Supplier PartAuxiliary ID",
    "Amount/UOM & UOM",
    "Product Size",
    "Product Description",
    "Shipping Method",
    "Carrier",
    "LineItem Notes",
    "Non Catalog",
    "Product Type",
    "Supplier Duns No",
    "Supplier Phone",
    "Contract No",
    "Contract Renewal No",
    "Contract Name",
    "Contract Effective Date",
    "Contract Expiration Date",
    "Contract Unit Price",
    "Contract Unit Price Variance",
    "FormId",
    "Replenishment Order",
    "Stock Item ID",
    "Stock Item Name",
    "Stock Units",
    "Stock Supplier Name",
    "Stock Supplier ID",
    "Stock FC Name",
    "Stock FC ID",
    "Line Status",
    "Manufacturer",
    "Mfr Catalog #",
    "Category Preference",
    "Category Level 1",
    "Category Level 2",
    "Category Level 3",
    "Category Level 4",
    "Category Level 5",
    "Category Name",
    "CAS #",
    "UNSPSC",
    "Commodity Code",
    "Shipping Charge",
    "Tax 1",
    "Tax 2",
    "DMR_MatchType",
    "Flex Field 1",
    "Contract Number",
    "Flex Pull 2",
    "Flex Pull 1",
    "Freight Terms",
    "Flex Field 2",
    "Reference Number",
    "Order Delivery",
    "Price Set Name",
    "Consortium Spend",
    "Original Requisition ID",
    "Original Requisition Name",
    "Original Requisition Requestor",
    "Payment Transaction ID|Payment Transaction Amount",
]

PAYMENTS_HDR_SUBSET = [
    "PO ID",
    "Creation Date",
    "PO #",
    "PR ID",
    "Buyer: Email",
    "Supplier ID",
    "Supplier Name",
    "Supplier Number",
    "Supplier Duns No",
    "PO Line #",
    "Quantity",
    "Unit Price",
    "Extended Price",
    "Currency",
    "SKU/Catalog #",
    "Supplier PartAuxiliary ID",
    "Amount/UOM & UOM",
    "Product Description",
    "Manufacturer",
    "Mfr Catalog #",
    "Category Level 1",
    "Category Level 2",
    "Category Level 3",
    "Category Level 4",
    "Category Level 5",
    "UNSPSC",
]

PRICE_COLS = ["Unit Price", "Extended Price"]

# TODO - Probably use this to load where needed and only preprocess when files are missing
def load_transactions():
    click.echo("Loading transaction data...")
    if not os.path.exists(TRANSATIONS_PATH):
        process_all_csvs()
    return pd.read_csv(
            TRANSATIONS_PATH,
            encoding='ISO-8859-1',
            header=0,
            dtype={
                "PR ID": str
            },
            parse_dates=["Creation Date"]
        )

def process_all_csvs(input_dir=TRANSACTION_DIR, output_path=TRANSATIONS_PATH, chunksize=100000):
    """Processes all files (specifically transaction files) into a standard format for the rest of the application.
    
    This is intended to be run prior to deploying the tabpy functions so as to reduce performance impact.

    Args:
        input_dir (str, optional): Path to the directory with transation csvs. Defaults to TRANSACTION_DIR.
        output_path (str, optional): Path to the combined file output. Defaults to TRANSATIONS_PATH.
        chunksize (int, optional): Chunk limit in case of IO limits. Defaults to 100000.
    """
    click.echo("Processing files...")
    all_files = glob.glob(os.path.join(input_dir, "*.csv"))

    # Chunking file IO for caution
    with open(output_path, "w", encoding="utf-8") as master_file:
        first_file = True

        for file_path in tqdm(all_files):
            click.echo(f"Processing: {file_path}")
            for chunk in pd.read_csv(
                file_path,
                chunksize=chunksize,
                encoding="ISO-8859-1",
                header=0,
                names=PAYMENTS_HDR,
                usecols=PAYMENTS_HDR_SUBSET,
                parse_dates=["Creation Date"],
                dtype={"PR ID": str},
                low_memory=False,
            ):
                cleaned_chunk = _clean_chunk(chunk)
                cleaned_chunk.to_csv(
                    master_file,
                    index=False,
                    header=first_file,  # Only write header for first file
                    mode="a",
                )
                first_file = False


def _clean_chunk(chunk: pd.DataFrame):
    # TODO - Some product descriptions have html in them; could stand for cleaning
    for col in PRICE_COLS:
        _price_column_to_float(chunk, col)

    # Specific handling of annoying columns
    chunk["PR ID"] = chunk["PR ID"].astype(str)
    chunk["Supplier Duns No"] = chunk["Supplier Duns No"].astype(str)

    return chunk


def _price_column_to_float(df: pd.DataFrame, col: str):
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(r"[^\d\.\-]", "", regex=True)
        .replace("", pd.NA)
        .astype(float)
    )

def prepare_clustered_data(output_dir: str = OUTPUT_DIR) -> None:
    # It would be better to not load things twice, but I like the benefit of consolidating the files first
    df = load_transactions()
    embeddings = compute_embeddings(df['Product Description'])
    df['Cluster'] = cluster_embeddings(embeddings)
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(TRANSATIONS_PATH, index=False)
    np.save(EMBEDDINGS_PATH, embeddings)

def compute_embeddings(texts):
    click.echo("Computing embeddings...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model.encode(texts.tolist(), show_progress_bar=True)

def cluster_embeddings(embeddings, n_clusters=10) -> np.ndarray:
    click.echo("Fitting clusters....")
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    return model.fit_predict(embeddings)


# TODO -- DO I NEED TO DROP 0 unit prices??
# def clean_po_data(df):
#     df = df.dropna(subset=['Product Description', 'Supplier Name', 'Unit Price'])
#     df = df[df['Unit Price'] != 0]
#     df['Unit Price'] = pd.to_numeric(df['Unit Price'], errors='coerce')
#     return df
