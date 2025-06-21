import React, { useState } from 'react';

const VideoPlayer = ({ videoUrl, videoId, onDownload }) => {
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const handleTimeUpdate = (e) => {
    setCurrentTime(e.target.currentTime);
  };

  const handleLoadedMetadata = (e) => {
    setDuration(e.target.duration);
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleDownload = () => {
    if (onDownload) {
      onDownload();
    } else {
      // Fallback download method
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = `video_${videoId}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="relative">
        <video
          className="w-full h-auto max-h-96 object-contain bg-black"
          controls
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
        >
          <source src={videoUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>
      
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Generated Video</h3>
            <p className="text-sm text-gray-500">ID: {videoId}</p>
          </div>
          <button
            onClick={handleDownload}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-medium transition-colors flex items-center space-x-2"
          >
            <span>📥</span>
            <span>Download MP4</span>
          </button>
        </div>
        
        <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
          <div>
            <p>Duration: {formatTime(duration)}</p>
            <p>Format: MP4</p>
          </div>
          <div className="text-right">
            <p>Status: Ready</p>
            <p>Quality: HD</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer; 