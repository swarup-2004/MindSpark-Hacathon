# Tactical Trends Backend



This project is part of the MindSpark Hackathon and involves building a news aggregation application using a Django backend, integrated with Qdrant for vector storage and MySQL for data management.

## Getting Started

### Prerequisites

Ensure that you have the following installed:

- **Python 3.11**
- **pip** (Python package installer)
- **virtualenv** (optional but recommended)
- **Docker** (for Qdrant)
- **MySQL** (for the database)

### 1. Clone the Repository

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/swarup-2004/MindSpark-Hacathon.git
cd MindSpark-Hacathon
```

### 2. Set Up a Virtual Environment

Create and activate a virtual environment:

```bash
# Create a virtual environment
python -m venv env

# Activate the virtual environment
# For Windows:
env\Scripts\activate
# For Mac/Linux:
source env/bin/activate
```

### 3. Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Qdrant Vector Database

#### Pull the Docker Image from Docker Hub:

```bash
docker pull qdrant/qdrant
```

#### Run the Qdrant Docker Image:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

#### Create a Collection:

In a Python script or interactive shell, run the following code:

```python
from qdrant_client import QdrantClient

client = QdrantClient("http://localhost:6333")

def create_qdrant_collection():
    collection_name = "articles"
    # Check if the collection exists
    client.create_collection(
        collection_name=collection_name,
        vectors_config={"size": 384, "distance": "Cosine"}  # Adjust the vector size as per your model
    )
    print(f"Collection '{collection_name}' created.")

create_qdrant_collection()
```

### 5. Configure the MySQL Database

1. Create a database named `news` on your local MySQL server.
2. Create a `.env` file in your project directory and add the following configurations:

```
DATABASE_NAME=news
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=localhost
DATABASE_PORT=3306

EMAIL_PORT=your_email_port
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email_host_user
EMAIL_HOST_PASSWORD=your_email_host_password
DEFAULT_FROM_EMAIL=your_default_from_email

NEWS_API_KEY=your_news_api_key
```

### 6. Migrate the Database

Change to the `mindspark_backend` directory and run migrations:

```bash
cd mindspark_backend
python manage.py migrate
```

### 7. Create a Superuser

Create a superuser for the Django admin interface:

```bash
python manage.py createsuperuser
```

### 8. Run the Server

Start the Django development server:

```bash
python manage.py runserver
```

## Additional Notes

- Ensure that you have Docker installed and running on your machine to pull and run the Qdrant image.
- Make sure to replace placeholder values in the `.env` file with your actual database and email configuration details.
