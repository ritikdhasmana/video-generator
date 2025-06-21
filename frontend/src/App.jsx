import React, { useState } from 'react';
import Generator from './pages/Generator';
import VideoGallery from './components/VideoGallery';
import Navigation from './components/Navigation';

function App() {
  const [activeTab, setActiveTab] = useState('generator');

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="py-8">
        {activeTab === 'generator' ? (
          <Generator />
        ) : (
          <div className="max-w-6xl mx-auto px-4">
            <VideoGallery />
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 