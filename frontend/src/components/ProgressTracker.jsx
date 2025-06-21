import React, { useState, useEffect, useRef } from 'react';
import { videoService } from '../services/api';
import VideoPlayer from './VideoPlayer';

const ProgressTracker = ({ videoId, onComplete }) => {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [showVideo, setShowVideo] = useState(false);
  const intervalRef = useRef(null);

  const saveVideoToGallery = (videoData) => {
    try {
      const existingVideos = JSON.parse(localStorage.getItem('generatedVideos') || '[]');
      const newVideo = {
        id: videoId,
        url: videoService.getVideoPreviewUrl(videoId),
        createdAt: new Date().toISOString(),
        status: videoData.status,
        progress: videoData.progress
      };

      // Check if video already exists
      const existingIndex = existingVideos.findIndex(v => v.id === videoId);
      if (existingIndex >= 0) {
        existingVideos[existingIndex] = newVideo;
      } else {
        existingVideos.unshift(newVideo); // Add to beginning
      }

      localStorage.setItem('generatedVideos', JSON.stringify(existingVideos));
    } catch (err) {
      console.error('Failed to save video to gallery:', err);
    }
  };

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const checkStatus = async () => {
    try {
      const response = await videoService.getVideoStatus(videoId);
      setStatus(response);

      if (response.status === 'completed') {
        onComplete && onComplete(response);
        setShowVideo(true);
        saveVideoToGallery(response);
        stopPolling();
        return true;
      } else if (response.status === 'failed') {
        setError('Video generation failed');
        stopPolling();
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error checking status:', err);
      if (err.response?.status === 404) {
        setError(`Video ID ${videoId} not found. The video may have been lost due to server restart.`);
        stopPolling();
        return true;
      } else {
        setError('Failed to check status');
      }
      return false;
    }
  };

  useEffect(() => {
    // Check status immediately
    checkStatus();

    // Start polling
    intervalRef.current = setInterval(async () => {
      const shouldStop = await checkStatus();
      if (shouldStop) {
        stopPolling();
      }
    }, 2000);

    // Cleanup on unmount
    return () => {
      stopPolling();
    };
  }, [videoId]);

  const handleDownload = async () => {
    try {
      const blob = await videoService.downloadVideo(videoId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `video_${videoId}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
      // Fallback to direct download
      window.open(videoService.getVideoPreviewUrl(videoId), '_blank');;
    }
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <p className="text-blue-600">Checking status...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-md p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Video Generation Progress</h3>

        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span>{status.progress || 0}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${status.progress || 0}%` }}
              ></div>
            </div>
          </div>

          <div className="text-sm text-gray-600">
            <p>Status: <span className="font-medium">{status.status}</span></p>
            <p>Video ID: <span className="font-mono">{videoId}</span></p>
          </div>

          {status.status === 'completed' && (
            <div className="bg-green-50 border border-green-200 rounded-md p-4">
              <p className="text-green-800 font-medium">Video generation completed!</p>
              <div className="mt-3 flex space-x-3">
                <button
                  onClick={() => setShowVideo(!showVideo)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  {showVideo ? 'Hide Preview' : 'Preview Video'}
                </button>
                <button
                  onClick={handleDownload}
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
                >
                  Download Video
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Video Preview Section */}
      {showVideo && status.status === 'completed' && (
        <div className="bg-white border border-gray-200 rounded-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Video Preview</h3>
          <VideoPlayer
            videoUrl={videoService.getVideoPreviewUrl(videoId)}
            videoId={videoId}
            onDownload={handleDownload}
          />
        </div>
      )}
    </div>
  );
};

export default ProgressTracker; 