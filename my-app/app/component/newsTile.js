'use client'

import React from 'react';

const NewsTile = ({ title, url }) => {
  return (
    <div className="border border-gray-200 rounded-lg p-4 mb-4 shadow-md hover:shadow-lg transition-shadow">
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:underline"
      >
        Read More
      </a>
    </div>
  );
};

export default NewsTile;