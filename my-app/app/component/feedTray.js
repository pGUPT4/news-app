// components/FeedTray.js
'use client';

import React, { useState, useEffect } from 'react';
import NewsTile from './newsTile';

const FeedTray = () => {
  const [newsItems, setNewsItems] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('https://news-recommender-backend-20d530136c15.herokuapp.com/news-galore');
        if (!response.ok) {
          throw new Error('Failed to fetch news');
        }
        const data = await response.json();
        setNewsItems(data); 
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchNews();
}, []);

// useEffect(() => {
//     const fetchNews = async () => {
//         try {
//             const response = await fetch('https://news-recommender-backend-env.eba-pwgqwnyf.us-east-2.elasticbeanstalk.com/news-galore');
//             if (!response.ok) throw new Error('Failed to fetch news');
//             const data = await response.json();
//             setNews(data.error ? [] : data);
//             setError(data.error || data.fetch_error || null);
//         } catch (err) {
//             setError(err.message);
//         }
//     };
//     fetchNews();
//   }, []);

  
  
  
  return (
    <div className="flex justify-center min-h-screen">
      <div className="mt-20 w-full max-w-[1150px] h-[900px] bg-gray-400 rounded-lg p-4 overflow-y-auto">
        {loading ? (
          <div className="text-gray-800 text-center">Loading news...</div>
        ) : error ? (
          <div className="text-red-900 text-center">Error: {error}</div>
        ) : (
          <div className="flex flex-wrap gap-4 justify-center">
          {newsItems.map((item, index) => (
            <NewsTile key={index} title={item.title} url={item.url} />
          ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedTray;