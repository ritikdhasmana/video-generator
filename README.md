# Video AI Generator

An AI-powered video generation system that creates engaging social media videos from product URLs using AI-generated content and dynamic templates.

## Features

- AI Video Generation: Transform product URLs into engaging social media videos
- Multiple Templates: 6 beautiful video templates with vibrant colors and modern typography
- AI Content Generation: Automatic script generation using Hugging Face models
- Dynamic Slideshows: Animated image slideshows with smooth transitions
- Multi-Format Support: 16:9 and 9:16 aspect ratios for different platforms
- High Visibility Text: Bright, readable text overlays on any background

## Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg
- Hugging Face API key (free at https://huggingface.co/settings/tokens)

## Quick Start

### 1. Install FFmpeg

macOS:

brew install ffmpeg


Ubuntu/Debian:

sudo apt update && sudo apt install ffmpeg


Windows:
Download from https://ffmpeg.org/download.html

### 2. Set Up Backend


cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip3 install -r requirements.txt
cp env.example .env


Edit backend/.env and add your Hugging Face API key:

HUGGINGFACE_API_KEY=your_api_key_here
HUGGINGFACE_MODEL=meta-llama/Llama-3.1-8B-Instruct


Create storage directories:

mkdir -p ./storage/videos ./storage/images ./storage/video_status


### 3. Set Up Frontend


cd ../frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env


### 4. Run the Application

Terminal 1 - Backend:

cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


Terminal 2 - Frontend:

cd frontend
npm run dev


### 5. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Usage

1. Enter a product URL (supports Amazon, Shopify, and other e-commerce sites)
2. Select a video template
3. Choose aspect ratio (16:9 or 9:16)
4. Set video duration (15-60 seconds)
5. Click "Generate Video"
6. Wait for processing and download your video

## Video Templates

1. High Visibility - Maximum contrast for any background
2. Modern Bold - Orange to Pink gradient with bold typography
3. Elegant Professional - Blue gradient with clean, professional look
4. Bold Action - High-energy orange gradient for action content

## API Endpoints

- POST /api/v1/video/generate - Generate video from product URL
- GET /api/v1/video/{video_id} - Get video generation status
- GET /api/v1/video/{video_id}/download - Download generated video
- GET /api/v1/video/templates - List available video templates

## Troubleshooting

### Common Issues

1. FFmpeg not found: Install FFmpeg using the commands above
2. Port conflicts: Change ports in .env files if needed
3. API key issues: Verify your Hugging Face API key is correct
4. Dependencies issues: Reinstall with pip install -r requirements.txt or npm install

## Docker Deployment (Not working)

For Docker deployment, use:

cp env.template .env
# Edit .env with your API keys
docker-compose up -d