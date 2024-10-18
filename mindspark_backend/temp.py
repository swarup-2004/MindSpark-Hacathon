from qdrant_client import QdrantClient

client = QdrantClient("http://localhost:6333")

def create_qdrant_collection(collection_name):
    # Create collection with valid settings
    client.create_collection(
        collection_name=collection_name,
        vectors_config={"size": 384, "distance": "Cosine"},
        shard_number=4  # Adjust the shard number as needed
    )
    print(f"Collection '{collection_name}' created.")

create_qdrant_collection("articles")