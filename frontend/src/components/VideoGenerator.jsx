import React, { useState, useEffect } from 'react';
import { videoService } from '../services/api';
import ProgressTracker from './ProgressTracker';

const VideoGenerator = () => {
  const [url, setUrl] = useState('');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [duration, setDuration] = useState(30);
  const [template, setTemplate] = useState('modern_bold');
  const [templates, setTemplates] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoId, setVideoId] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load available templates
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await videoService.getTemplates();
      setTemplates(response.templates || []);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setError('Please enter a product URL');
      return;
    }

    setError(null);
    setIsGenerating(true);
    setVideoId(null);

    try {
      const response = await videoService.generateVideo({
        url: url.trim(),
        aspect_ratio: aspectRatio,
        duration: duration,
        template: template
      });
      
      setVideoId(response.video_id);
      console.log('Video generation started:', response);
    } catch (err) {
      console.error('Failed to generate video:', err);
      setError(err.response?.data?.detail || 'Failed to generate video');
      setIsGenerating(false);
    }
  };

  const handleComplete = () => {
    setIsGenerating(false);
    // Optionally reset form or show success message
  };

  const handleGenerateNew = () => {
    setVideoId(null);
    setIsGenerating(false);
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          🎬 AI Video Generator
        </h1>
        
        <p className="text-gray-600 mb-8 text-center">
          Transform any product URL into an engaging social media video with AI-generated content and stunning visuals.
        </p>

        {!videoId ? (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* URL Input */}
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                Product URL *
              </label>
              <input
                type="url"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://amazon.com/product/..."
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* Template Selection */}
            <div>
              <label htmlFor="template" className="block text-sm font-medium text-gray-700 mb-2">
                Video Template
              </label>
              <select
                id="template"
                value={template}
                onChange={(e) => setTemplate(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {templates.map((t) => (
                  <option key={t.name} value={t.name.toLowerCase().replace(/\s+/g, '_')}>
                    {t.name} - {t.description}
                  </option>
                ))}
              </select>
              <p className="text-sm text-gray-500 mt-1">
                Choose a visual style for your video
              </p>
            </div>

            {/* Aspect Ratio */}
            <div>
              <label htmlFor="aspectRatio" className="block text-sm font-medium text-gray-700 mb-2">
                Aspect Ratio
              </label>
              <select
                id="aspectRatio"
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="16:9">16:9 - Landscape (YouTube, Facebook)</option>
                <option value="9:16">9:16 - Portrait (Instagram, TikTok)</option>
              </select>
            </div>

            {/* Duration */}
            <div>
              <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-2">
                Duration (seconds)
              </label>
              <input
                type="number"
                id="duration"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                min="15"
                max="60"
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-sm text-gray-500 mt-1">
                Recommended: 15-30 seconds for social media
              </p>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <p className="text-red-600">{error}</p>
              </div>
            )}

            {/* Generate Button */}
            <button
              type="submit"
              disabled={isGenerating}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isGenerating ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Starting Generation...
                </span>
              ) : (
                'Generate Video'
              )}
            </button>
          </form>
        ) : (
          <div className="space-y-6">
            <ProgressTracker videoId={videoId} onComplete={handleComplete} />
            
            <div className="flex justify-center">
              <button
                onClick={handleGenerateNew}
                className="bg-gray-600 text-white px-6 py-3 rounded-md hover:bg-gray-700 transition-colors"
              >
                Generate New Video
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoGenerator; 