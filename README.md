# Video Frame Extractor with Metadata Editor

A web application for extracting frames from videos and managing image metadata, built with Vue.js and Flask.

## Features

### Video Processing
- Extract frames from videos at specified intervals
- Customizable frame extraction settings:
  - Frame interval (1-30 seconds)
  - Maximum number of frames (up to 100)
- Batch download selected frames
- Download frames as ZIP for multiple selections
- Supports various video formats (MP4, AVI, MOV)
- 2-minute video duration limit

### Image Metadata
- Read EXIF metadata from images
  - Camera information (make, model, lens)
  - GPS coordinates
  - Capture settings (aperture, exposure, ISO)
  - Date and time information
- Write GPS metadata to images
  - Input coordinates manually
  - Select location from interactive map
  - Use current device location
  - View location on Google Maps

## Project Structure

```
├── client/                 # Frontend Vue.js application
│   ├── src/
│   │   ├── views/         # Vue components for each page
│   │   ├── router/        # Vue Router configuration
│   │   └── ...
│   ├── public/
│   └── package.json
│
├── server/                 # Backend Flask application
│   ├── helpers/           # Helper classes for video and metadata processing
│   ├── app.py             # Main Flask application
│   └── requirements.txt   # Python dependencies
│
└── README.md
```

## Technologies Used

### Frontend
- Vue.js 3
- Vue Router
- Tailwind CSS
- Axios
- Leaflet (for maps)
- JSZip (for batch downloads)

### Backend
- Flask
- OpenCV (video processing)
- Pillow (image processing)
- ExifRead (metadata handling)

## Setup and Installation

### Frontend Setup
```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Run development server
npm run dev
```

### Backend Setup
```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
```

## API Endpoints

### Video Processing
- `POST /split-video`
  - Extract frames from video
  - Parameters:
    - video: Video file
    - frame_interval: Interval between frames (seconds)
    - max_frames: Maximum number of frames to extract

### Metadata
- `POST /read-metadata`
  - Read EXIF metadata from image
  - Parameters:
    - image: Image file

- `POST /write-metadata`
  - Write GPS metadata to image
  - Parameters:
    - image: Image file
    - metadata: GPS coordinates and references

## Browser Support
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Authors
Miftahul Huda - Initial work

## Acknowledgments
- OpenCV team for video processing capabilities
- ExifRead developers for metadata handling
- Vue.js and Flask communities for excellent documentation
