import React, { useState, useEffect } from 'react';
import { videoService } from '../services/api';

const VideoGallery = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      setLoading(true);
      // This would need a backend endpoint to list all videos
      // For now, we'll use localStorage to track generated videos
      const savedVideos = JSON.parse(localStorage.getItem('generatedVideos') || '[]');
      setVideos(savedVideos);
    } catch (err) {
      setError('Failed to load videos');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (videoId) => {
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
    }
  };

  const handleDelete = (videoId) => {
    const updatedVideos = videos.filter(video => video.id !== videoId);
    setVideos(updatedVideos);
    localStorage.setItem('generatedVideos', JSON.stringify(updatedVideos));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading videos...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg mb-4">No videos generated yet</div>
        <p className="text-gray-400">Generate your first video to see it here!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Your Generated Videos</h2>
        <button
          onClick={loadVideos}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Refresh
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos.map((video) => (
          <div key={video.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="relative">
              <video
                className="w-full h-48 object-cover"
                controls
                preload="metadata"
              >
                <source src={video.url} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
              
              <button
                onClick={() => handleDelete(video.id)}
                className="absolute top-2 right-2 bg-red-600 text-white p-1 rounded-full hover:bg-red-700 transition-colors"
                title="Delete video"
              >
                ×
              </button>
            </div>
            
            <div className="p-4">
              <h3 className="font-semibold text-gray-900 mb-2">
                Video {video.id}
              </h3>
              <p className="text-sm text-gray-600 mb-3">
                Generated: {new Date(video.createdAt).toLocaleDateString()}
              </p>
              
              <button
                onClick={() => handleDownload(video.id)}
                className="w-full bg-green-600 text-white px-3 py-2 rounded-md hover:bg-green-700 transition-colors text-sm"
              >
                Download Video
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VideoGallery; 