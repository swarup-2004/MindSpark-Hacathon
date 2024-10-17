import React, { useState } from "react";

function EverythingCard(props) {
  // State for likes and rating
  const [likes, setLikes] = useState(0);
  const [rating, setRating] = useState(0);

  // Function to handle like button click
  const handleLike = () => {
    setLikes(likes + 1);
  };

  // Function to handle rating click
  const handleRating = (newRating) => {
    setRating(newRating);
  };

  return (
    <div className="everything-card mt-20" onClick={props.onClick} style={{ cursor: 'pointer' }}>
      <div className="everything-card flex flex-wrap p-5 gap-1 mb-1">
        <b className="title">{props.title}</b>
        <div className="everything-card-img mx-auto">
          <img className="everything-card-img" src={props.imgUrl} alt="img" />
        </div>
        <div className="description">
          <p className="description-text leading-7">
            {props.description?.substring(0, 200)} {/* Truncate description */}
          </p>
        </div>
        <div className="info">
          <div className="source-info flex items-center gap-2">
            <span className="font-semibold">Source:</span>
            <a
              href={props.url}
              target="_blank"
              className="link underline break-words"
              rel="noopener noreferrer" // Recommended for security
            >
              {props.source.substring(0, 70)}
            </a>
          </div>
          <div className="origin flex flex-col">
            <p className="origin-item">
              <span className="font-semibold">Author:</span>
              {props.author}
            </p>
            <p className="origin-item">
              <span className="font-semibold">Published At:</span>
              ({props.publishedAt})
            </p>
          </div>
        </div>
      </div>

      {/* New Like and Rating System */}
      <div className="flex items-center gap-4 mt-4">
        {/* Like Button */}
        <button
          onClick={handleLike}
          className="like-btn px-3 py-2 bg-blue-500 text-white rounded"
        >
          👍 Like {likes}
        </button>

        {/* Rating System */}
        <div className="rating flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <span
              key={star}
              onClick={() => handleRating(star)}
              className={`cursor-pointer ${rating >= star ? "text-yellow-500" : "text-gray-400"}`}
            >
              ★
            </span>
          ))}
        </div>
        <span className="text-sm">Rating: {rating}/5</span>
      </div>

      {/* Additional Card Content */}
      <div className="flex lg:flex-row mt-4">
        <div
          className="h-48 lg:h-auto lg:w-48 flex-none bg-cover rounded-t lg:rounded-t-none lg:rounded-l text-center overflow-hidden"
          style={{ backgroundImage: `url(${props.imageUrlLeft})` }}
          title={props.imageLeftTitle}
        ></div>
        <div className="border rounded-b lg:rounded-b-none lg:rounded-r p-4 flex flex-col justify-between leading-normal">
          <div className="mb-8">
            <p className="text-sm text-gray-600 flex items-center">
              {props.memberIcon && (
                <svg
                  className="fill-current text-gray-500 w-3 h-3 mr-2"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                >
                  {props.memberIcon}
                </svg>
              )}
              {props.memberText}
            </p>
            <div className="text-gray-900 font-bold text-xl mb-2">
              {props.cardTitle}
            </div>
            <p className="text-gray-700 text-base">{props.cardDescription}</p>
          </div>
          <div className="flex items-center">
            {props.authorImage && (
              <img
                className="w-10 h-10 rounded-full mr-4"
                src={props.authorImage}
                alt="Avatar"
              />
            )}
            <div className="text-sm">
              <p className="text-gray-900 leading-none">{props.authorName}</p>
              <p className="text-gray-600">{props.publishedDate}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EverythingCard;
