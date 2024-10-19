## Repositories and Resources

### Backend Repository
- **Link**: [NeuralKnights Gold Root Backend](https://github.com/swarup-2004/NeuralKnights-Gold-Root-Backend-.git)

### Frontend Repository
- **Link**: [NeuralKnights Gold Frontend](https://github.com/Virucodes/NeuralKnights-Gold-Front-end.git)

### Chrome Extension Repository
- **Link**: [NeuralKnights Gold Chrome Extension](https://github.com/Virucodes/NeuralKnights-Gold-Chrome-Extension.git)

### Dataset
- **Link**: [Global News Dataset (Kaggle)](https://www.kaggle.com/datasets/everydaycodings/global-news-dataset)

# Web Portal Video Link:
# Chrome Extension Video Link:  



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
- **Node** (for the frontend)

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

To configure Qdrant and store collections on the local disk when running it via Docker, you can follow these updated steps:

### 4. Configure Qdrant Vector Database with Local Storage

### Pull the Qdrant Docker Image from Docker Hub

```bash
docker pull qdrant/qdrant
```

#### Run the Qdrant Docker Image with Local Disk Storage

To store the Qdrant collection data on your local disk, map a local directory to a directory inside the Docker container.

```bash
docker run -p 6333:6333 \
  -v /path/to/local/storage:/qdrant/storage \
  qdrant/qdrant
```

In the command above:

- Replace `/path/to/local/storage` with the actual path where you want to store the Qdrant collections on your local machine. For example, `C:\Users\YourName\Documents\QdrantData` on Windows or `/home/yourname/qdrant_data` on Linux/macOS.
- The `-v` option mounts the specified local directory to `/qdrant/storage` inside the Docker container, which is the default storage path for Qdrant.


#### Create a Collection:

In a Python script or interactive shell, run the following code:

```python
from qdrant_client import QdrantClient

client = QdrantClient("http://localhost:6333")

def create_qdrant_collection(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config={"size": 384, "distance": "Cosine"}  # Adjust the vector size as per your model
    )
    print(f"Collection '{collection_name}' created.")

create_qdrant_collection("articles")
create_qdrant_collection("keywords")
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

### 8. Update `CORS_ALLOWED_ORIGINS` 
In your `settings.py` file, update the `CORS_ALLOWED_ORIGINS` setting to include the URL of your frontend application. This ensures that cross-origin requests from your frontend to the backend are allowed.

```python
CORS_ALLOWED_ORIGINS = [
    'http://your-frontend-url.com',  # Replace with your actual frontend URL
]
```

This setting ensures that only the specified frontend domain is allowed to interact with your backend via cross-origin requests.

---

### 9. Update "domain" and "name" in the `django_site` Table
In your database, specifically the `django_site` table, update the following fields:

- **`domain`**: Set this to your frontend domain.
- **`name`**: Set this to your application's name.

You can do this either by:
1. Accessing the `django_site` table directly in your database and updating the fields manually.
2. Using the Django admin panel, which can be accessed after running the server.


### 10. Run the Server

Start the Django development server:

```bash
python manage.py runserver
```



### 8. Run the Server

Start the React server:

```bash
npm run dev
```

## Additional Notes

- Ensure that you have Docker installed and running on your machine to pull and run the Qdrant image.
- Make sure to replace placeholder values in the `.env` file with your actual database and email configuration details.
