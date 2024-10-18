from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from .models import Article  # Assuming you're working with an Article model
from qdrant_client.http.models import Filter, SearchRequest
from sentence_transformers import SentenceTransformer
from .models import Article, UserActivityLogs  # Assuming you have the Article model

# Load the model again (if not already loaded)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
client = QdrantClient("http://localhost:6333")


def similarity_search_using_keyword(keyword):
    # Create the query string for the keyword
    query_string = f"Give me articles related to the word '{keyword}'"

    print(keyword)
    
    # Encode the query string into a vector
    vector = model.encode(query_string)

    # Query Qdrant to find the most similar articles
    response = client.search(
        collection_name="articles",
        query_vector=vector.tolist(),
        limit=20,  # Limit the number of results
    )

    # Extract article IDs from the search results
    similar_article_ids = [result.payload.get("id") for result in response]
    print(similar_article_ids)

    return similar_article_ids





def add_keyword(keyword_id):
    # Retrieve the keyword from your Django model
    keyword = UserActivityLogs.objects.get(id=keyword_id)

    # Encode the keyword to get its vector representation
    vector = model.encode(keyword.keyword)

    # Prepare the payload, associating it with the keyword id
    payload = [
        {
            "id": keyword_id,
            "keyword": keyword.keyword
        }
    ]

    # Upload the single vector and its associated payload to the "keywords" collection in Qdrant
    client.upload_collection(
        collection_name="keywords",
        vectors=[vector.tolist()],  # Ensure vector is a list of floats and wrapped inside a list
        payload=payload  # Payload must also be wrapped in a list
    )
    
    print(f"Keyword '{keyword.keyword}' added to Qdrant with ID {keyword_id}.")


    




def find_similar_keyword(keyword):
    # Convert keyword to vector
    try:
        vector = model.encode(keyword)
    except Exception as e:
        print(f"Error encoding keyword '{keyword}': {e}")
        return {"id": None, "score": 0}

    try:
        # Query Qdrant for the most similar keyword
        response = client.search(
            collection_name="keywords",
            query_vector=vector.tolist(),  # Convert numpy array to list if necessary
            limit=1  # Fetch only the most similar result
        )
        
        if response and len(response) > 0:  # Ensure there is a valid response
            result = response[0]
            return {
                "id": result.payload.get("id"),
                "score": result.score
            }
    except Exception as e:
        print(f"Error querying Qdrant: {e}")

    # Return default result if no match is found
    return {"id": None, "score": 0}




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
        vector = model.encode(article.full_content)
        vectors.append(vector)

        # Prepare the payload (additional metadata you want to store)
        payload = {
            "id": article.id,
        }
        payloads.append(payload)

    # Upload vectors and payloads to Qdrant
    client.upload_collection(
        collection_name="articles",
        vectors=vectors,
        payload=payloads
    )

    articles.update(transferred=True)



