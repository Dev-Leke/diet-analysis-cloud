"""
serverless_function.py
Task 3 - Step 2: The simulated serverless function.

Mimics an Azure Function that, in REAL Azure, would trigger automatically when
a blob is uploaded. Azurite can't fire triggers, so we invoke it manually.

It performs the three required steps:
  1. Reads All_Diets.csv FROM Azurite Blob Storage (simulated cloud storage)
  2. Cleans the data and computes average macros per diet type
  3. Writes the results to a JSON file (simulated NoSQL / Cosmos DB store)

Run it with:  python serverless_function.py
"""

import io
import os
import json
import pandas as pd
from azure.storage.blob import BlobServiceClient

# Same Azurite credentials as the upload script.
ACCOUNT_KEY = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    f"AccountKey={ACCOUNT_KEY};"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

CONTAINER_NAME = "datasets"
BLOB_NAME = "All_Diets.csv"
OUTPUT_DIR = "simulated_nosql"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.json")
MACROS = ["Protein(g)", "Carbs(g)", "Fat(g)"]


def process_nutritional_data():
    # --- 1. READ the CSV FROM blob storage (not from local disk this time) ---
    service = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    blob_client = service.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)

    print(f"Downloading '{BLOB_NAME}' from blob container '{CONTAINER_NAME}'...")
    stream = blob_client.download_blob().readall()    # raw bytes from "the cloud"
    df = pd.read_csv(io.BytesIO(stream))              # wrap bytes so pandas can read them
    print(f"Loaded {len(df)} rows from blob storage.")

    # --- 2. CLEAN + COMPUTE average macros per diet type ---
    df["Diet_type"] = df["Diet_type"].str.strip().str.lower()
    df[MACROS] = df[MACROS].apply(pd.to_numeric, errors="coerce")
    df[MACROS] = df[MACROS].fillna(df[MACROS].mean())

    avg_macros = df.groupby("Diet_type")[MACROS].mean().round(2)

    # --- 3. SHAPE as JSON documents (Cosmos-style) and STORE ---
    # orient="records" -> a list of {column: value} dicts, i.e. JSON documents.
    results = avg_macros.reset_index().to_dict(orient="records")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nStored {len(results)} documents in {OUTPUT_FILE}:")
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    process_nutritional_data()
