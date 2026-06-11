"""
upload_to_azurite.py
Task 3 - Step 1: Upload All_Diets.csv into Azurite's simulated Blob Storage.

This puts the CSV into a blob container called 'datasets', exactly as you would
upload a file to real Azure Blob Storage. Only the connection string differs.
"""

from azure.storage.blob import BlobServiceClient

# ---------------------------------------------------------------------------
# Azurite's WELL-KNOWN development connection string.
# This account name + key are PUBLIC and identical for every Azurite user.
# They are NOT secret and only unlock your local emulator, never real Azure.
# ---------------------------------------------------------------------------
ACCOUNT_KEY = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="

CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
   f"AccountKey= {ACCOUNT_KEY};"
    "kQ8cKSfV5z2xUiW8fa5b2qXgC4XnZ8Q1L1bGZ8Q==;"  # standard Azurite dev key
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

CONTAINER_NAME = "datasets"
LOCAL_FILE = "All_Diets.csv"
BLOB_NAME = "All_Diets.csv"   # the name it will have inside the container


def main():
    # 1. Connect to the (emulated) blob storage account.
    service = BlobServiceClient.from_connection_string(CONNECTION_STRING)

    # 2. Create the container if it doesn't already exist.
    container = service.get_container_client(CONTAINER_NAME)
    if not container.exists():
        container.create_container()
        print(f"Created container: {CONTAINER_NAME}")
    else:
        print(f"Container already exists: {CONTAINER_NAME}")

    # 3. Upload the local CSV as a blob (overwrite=True replaces it if re-run).
    with open(LOCAL_FILE, "rb") as data:
        container.upload_blob(name=BLOB_NAME, data=data, overwrite=True)
    print(f"Uploaded {LOCAL_FILE} -> {CONTAINER_NAME}/{BLOB_NAME}")

    # 4. List blobs in the container to PROVE the upload worked.
    print("\nBlobs now in container:")
    for blob in container.list_blobs():
        print(f"  - {blob.name} ({blob.size} bytes)")


if __name__ == "__main__":
    main()
