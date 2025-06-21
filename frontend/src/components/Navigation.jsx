import React from 'react';

const Navigation = ({ activeTab, onTabChange }) => {
  return (
    <div className="bg-white shadow-sm border-b">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex space-x-8">
          <button
            onClick={() => onTabChange('generator')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'generator'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            🎬 Generate Video
          </button>
          <button
            onClick={() => onTabChange('gallery')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'gallery'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            📁 Video Gallery
          </button>
        </div>
      </div>
    </div>
  );
};

export default Navigation; 