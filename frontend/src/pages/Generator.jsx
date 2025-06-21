import React, { useState } from 'react';
import UrlInput from '../components/UrlInput';
import ProgressTracker from '../components/ProgressTracker';
import { videoService } from '../services/api';

const Generator = () => {
  const [videoId, setVideoId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [completedVideo, setCompletedVideo] = useState(null);

  const handleUrlSubmit = async (url) => {
    try {
      setIsLoading(true);
      setError(null);
      setCompletedVideo(null);
      
      const result = await videoService.generateVideo(url);
      setVideoId(result.video_id);
    } catch (err) {
      console.error('Failed to generate video:', err);
      setError(err.response?.data?.detail || 'Failed to generate video');
    } finally {
      setIsLoading(false);
    }
  };

  const handleComplete = (status) => {
    console.log('Video generation completed:', status);
    setCompletedVideo(status);
  };

  const handleReset = () => {
    setVideoId(null);
    setCompletedVideo(null);
    setError(null);
  };

  return (
    <div className="max-w-6xl mx-auto px-4">
      {!videoId ? (
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Generate Your Video Ad
            </h1>
            <p className="text-lg text-gray-600">
              Enter a product URL to create a compelling video advertisement
            </p>
          </div>
          
          <UrlInput onSubmit={handleUrlSubmit} isLoading={isLoading} />
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600">{error}</p>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          <ProgressTracker videoId={videoId} onComplete={handleComplete} />
          
          {completedVideo && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-center space-y-4">
                <h3 className="text-xl font-semibold text-gray-900">
                  🎉 Video Generation Complete!
                </h3>
                <p className="text-gray-600">
                  Your video is ready for preview and download.
                </p>
                <button
                  onClick={handleReset}
                  className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors font-medium"
                >
                  Generate Another Video
                </button>
              </div>
            </div>
          )}
          
          {!completedVideo && (
            <div className="text-center">
              <button
                onClick={handleReset}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
              >
                Cancel & Start Over
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Generator; 