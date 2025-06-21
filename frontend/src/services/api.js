import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const videoService = {
  async generateVideo(url, options = {}) {
    const response = await api.post('/api/v1/video/generate', {
      url,
      aspect_ratio: options.aspect_ratio || '16:9',
      duration: options.duration || 30,
    });
    return response.data;
  },

  async getVideoStatus(videoId) {
    const response = await api.get(`/api/v1/video/${videoId}`);
    return response.data;
  },

  async downloadVideo(videoId) {
    try {
      const response = await api.get(`/api/v1/video/${videoId}/download`, {
        responseType: 'blob',
        timeout: 30000, // 30 second timeout for large files
      });
      return response.data;
    } catch (error) {
      console.error('Download error:', error);
      throw new Error('Failed to download video');
    }
  },

  async getVideoInfo(videoId) {
    const response = await api.get(`/api/v1/video/${videoId}/info`);
    return response.data;
  },

  // Helper method to get video URL for preview
  getVideoPreviewUrl(videoId) {
    return `${API_BASE_URL}/api/v1/video/${videoId}/download`;
  },

  async getTemplates() {
    const response = await api.get('/video/templates');
    return response.data;
  }
}; 