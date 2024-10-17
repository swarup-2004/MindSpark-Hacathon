from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from .models import Article  # Assuming you're working with an Article model
from qdrant_client.http.models import Filter, SearchRequest
from sentence_transformers import SentenceTransformer
from .models import Article  # Assuming you have the Article model

# Load the model again (if not already loaded)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
client = QdrantClient("http://localhost:6333")

def query_similar_articles(article_id):
    
    try:
        # Fetch the article from the database using the provided article_id
        article = Article.objects.get(id=article_id)
        
        # Convert the article content to a vector
        vector = model.encode(article.description)

        # Query Qdrant to find 5 most similar articles
        response = client.search(
            collection_name="articles",
            query_vector=vector.tolist(),   # Convert numpy array to list if needed
            limit=30,  # Limit to 5 results
            
        )

        

        # Extract and return the articles from the response
        similar_articles = []
        for result in response:
            similar_articles.append(result.payload.get("id"))
            # similar_articles.append({
            #     "id": result.payload.get("id"),
            #     "description": result.payload.get("description"),
            #     "score": result.score  # Optional: similarity score
            # })

        return similar_articles

    except Article.DoesNotExist:
        return {"error": "Article not found"}
    except Exception as e:
        return {"error": str(e)}


def create_qdrant_collection():
    collection_name = "articles"
    # Check if the collection exists

    client.create_collection(collection_name=collection_name,vectors_config={"size": 384, "distance": "Cosine"})
    print(f"Collection '{collection_name}' created.")
  

def transfer_articles_to_qdrant():
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    articles = Article.objects.filter(transferred=False)
    vectors = []
    payloads = []

    for article in articles:
        # Convert the article content to a vector
        vector = model.encode(article.content)
        vectors.append(vector)

        # Prepare the payload (additional metadata you want to store)
        payload = {
            "id": article.id,
            "title": article.title,
            "author": article.author,
            "description": article.description,
        }
        payloads.append(payload)

    # Upload vectors and payloads to Qdrant
    client.upload_collection(
        collection_name="articles",
        vectors=vectors,
        payload=payloads
    )

    articles.update(transferred=True)



