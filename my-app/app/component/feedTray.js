// components/FeedTray.js
'use client';

import React, { useState, useEffect } from 'react';
import NewsTile from './newsTile'; // Capitalized import

const FeedTray = () => {
  const [newsItems, setNewsItems] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/news-galore');
        if (!response.ok) {
          throw new Error('Failed to fetch news');
        }
        const data = await response.json();
        setNewsItems(data); // [{title, url}, ...]
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  return (
    <div className="flex justify-center">
      <div className="mt-20 w-[1400px] h-[900px] bg-gray-400 rounded-lg p-4 overflow-y-auto">
        {loading ? (
          <div className="text-gray-800 text-center">Loading news...</div>
        ) : error ? (
          <div className="text-red-900 text-center">Error: {error}</div>
        ) : (
          newsItems.map((item, index) => (
            <NewsTile key={index} title={item.title} url={item.url} /> // Capitalized NewsTile
          ))
        )}
      </div>
    </div>
  );
};

export default FeedTray;