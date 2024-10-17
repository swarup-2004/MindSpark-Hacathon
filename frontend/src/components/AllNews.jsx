import { React, useState, useEffect } from 'react';
import EverythingCard from './EverythingCard';
import Loader from './Loader';
import Modal from './Modal';

function AllNews() {
  const [data, setData] = useState([]);
  const [page, setPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [wordCloudData, setWordCloudData] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const pageSize = 12;

  const handleArticleClick = (articleId) => {
    console.log("Clicked article ID:", articleId);
    setIsModalOpen(true);
    setSelectedArticle(articleId);

    // Fetch sentiment analysis
    fetchSentimentData(articleId);
    
    // Fetch word cloud data
    fetchWordCloudData(articleId);
  };

  const fetchSentimentData = (articleId) => {
    const token = localStorage.getItem('token');

    fetch(`http://localhost:8000/api/sentiment/${articleId}/`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Failed to fetch sentiment data.');
      })
      .then((data) => {
        setSentimentData(data.sentiment);
      })
      .catch((error) => {
        console.error('Sentiment fetch error:', error);
      });
  };

  const fetchWordCloudData = (articleId) => {
    const token = localStorage.getItem('token');

    fetch(`http://localhost:8000/api/wordcloud/${articleId}/`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Failed to fetch word cloud data.');
      })
      .then((data) => {
        setWordCloudData(data.wordCloud); // Adjust according to the API response
      })
      .catch((error) => {
        console.error('Word Cloud fetch error:', error);
      });
  };

  const handlePrev = () => {
    if (page > 1) setPage(page - 1);
  };

  const handleNext = () => {
    if (page < Math.ceil(totalResults / pageSize)) setPage(page + 1);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedArticle(null);
    setSentimentData(null);
    setWordCloudData(null);
  };

  useEffect(() => {
    setIsLoading(true);
    setError(null);

    const token = localStorage.getItem('token');

    fetch(`http://localhost:8000/api/articles/?page=${page}&pageSize=${pageSize}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Network response was not ok');
      })
      .then((myJson) => {
        if (myJson.results) {
          setTotalResults(myJson.count); // API provides total results in `count`
          setData(myJson.results); // API results are in `results` key
        } else {
          setError(myJson.message || 'An error occurred');
        }
      })
      .catch((error) => {
        console.error('Fetch error:', error);
        setError('Failed to fetch news. Please try again later.');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [page]);

  return (
    <>
      {error && <div className="text-red-500 mb-4">{error}</div>}

      <div className="my-10 cards grid lg:place-content-center md:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 xs:grid-cols-1 xs:gap-4 md:gap-10 lg:gap-14 md:px-16 xs:p-3">
        {!isLoading ? (
          data.map((element, index) => (
            <EverythingCard
              key={index}
              title={element.title}
              description={element.description}
              imgUrl={element.url_to_image}
              publishedAt={element.published_at}
              url={element.url}
              author={element.author}
              source={element.source}
              onClick={() => handleArticleClick(element.id)} // Pass article ID when clicked
            />
          ))
        ) : (
          <Loader />
        )}
      </div>

      {isModalOpen && (
        <Modal show={isModalOpen} onClose={handleCloseModal}>
          <h2>Article ID: {selectedArticle}</h2>
          {sentimentData && <div>Sentiment Analysis: {sentimentData}</div>}
          {wordCloudData && <div>Word Cloud: {wordCloudData}</div>}
          {/* You can render the word cloud visualization here */}
        </Modal>
      )}
      
      {!isLoading && data.length > 0 && (
        <div className="pagination flex justify-center gap-14 my-10 items-center">
          <button
            disabled={page <= 1}
            className="pagination-btn text-center"
            onClick={handlePrev}
          >
            &larr; Prev
          </button>
          <p className="font-semibold opacity-80">
            {page} of {Math.ceil(totalResults / pageSize)}
          </p>
          <button
            className="pagination-btn text-center"
            disabled={page >= Math.ceil(totalResults / pageSize)}
            onClick={handleNext}
          >
            Next &rarr;
          </button>
        </div>
      )}
    </>
  );
}

export default AllNews;
