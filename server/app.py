from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import json

from helpers.ExifHelper import ExifHelper
from helpers.LocationHelper import LocationHelper
from helpers.VideoHelper import VideoHelper

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Configure CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/read-metadata', methods=['POST', 'OPTIONS'])
def upload_image():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    if 'image' not in request.files:
        return jsonify({'error': 'No image file found in the request'}), 400

    image_file = request.files['image']
    
    try:
        # Open image from blob (in-memory file object)
        image_bytes = image_file.read()
        
        # Extract EXIF metadata
        exif = ExifHelper()
        exif_data = exif.get_exif_data(image_bytes)
        
        if not exif_data:
            return jsonify({'message': 'No EXIF metadata found'}), 200

        return jsonify({'exif_data': exif_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/write-metadata', methods=['POST', 'OPTIONS'])
def write_metadata():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    if 'image' not in request.files:
        return jsonify({'error': 'No image file found in the request'}), 400

    image_file = request.files['image']
    metadata = request.form.to_dict()
    
    image_bytes = image_file.read()
    
    # Extract EXIF metadata
    exif = ExifHelper()
    exif_data = exif.write_exif_data(image_bytes, metadata)
    
    if not exif_data:
        return jsonify({'message': 'No EXIF metadata found'}), 200

    return jsonify({'exif_data': exif_data}), 200


@app.route('/split-video', methods=['POST', 'OPTIONS'])
def split_video():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    if 'video' not in request.files:
        return jsonify({'error': 'No video file found in the request'}), 400
    
    video_file = request.files['video']
    
    # Get optional parameters with defaults
    max_frames = int(request.form.get('max_frames', 30))
    frame_interval = int(request.form.get('frame_interval', 1))
    
    try:
        # Read video file bytes
        video_bytes = video_file.read()
        
        # Create VideoHelper instance
        video_helper = VideoHelper()
        
        # Get video metadata
        metadata = video_helper.get_video_metadata(video_bytes)
        
        # Split video into frames
        frames = video_helper.split_video_to_frames(video_bytes, max_frames, frame_interval)
        
        if not frames:
            return jsonify({'error': 'Failed to extract frames from video'}), 400
            
        return jsonify({
            'metadata': metadata,
            'frames': frames,
            'frame_count': len(frames)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/interpolate-path', methods=['POST', 'OPTIONS'])
def interpolate_path():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        # Validate video file
        if 'video' not in request.files:
            return jsonify({'error': 'No video file found in the request'}), 400
            
        video_file = request.files['video']
        
        # Get and validate frames_interval
        frames_interval = request.form.get('frames_interval')
        if not frames_interval:
            return jsonify({'error': 'frames_interval is required'}), 400
        try:
            frames_interval = int(frames_interval)
            if frames_interval <= 0:
                return jsonify({'error': 'frames_interval must be positive'}), 400
        except ValueError:
            return jsonify({'error': 'frames_interval must be a number'}), 400
            
        # Get and validate timestamp data
        timestamp_data = request.form.get('timestamp')
        if not timestamp_data:
            return jsonify({'error': 'timestamp data is required'}), 400
            
        try:
            points = json.loads(timestamp_data)
            if not isinstance(points, list):
                return jsonify({'error': 'timestamp data must be a list'}), 400
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON format in timestamp data'}), 400
            
        # Create helpers
        video_helper = VideoHelper()
        location_helper = LocationHelper()
        
        # Validate timestamp format
        if not location_helper.validate_timestamps(points):
            return jsonify({'error': 'Invalid timestamp format. Use MMSS format'}), 400
            
        # Get video metadata
        video_bytes = video_file.read()
        metadata = video_helper.get_video_metadata(video_bytes)
        
        if not metadata:
            return jsonify({'error': 'Failed to read video metadata'}), 400
            
        # Check video duration (2 min limit)
        if metadata.get('duration', 0) > 120:  # 120 seconds = 2 minutes
            return jsonify({'error': 'Video duration exceeds 2 minutes limit'}), 400
            
        # Interpolate locations
        interpolated_points = location_helper.interpolate_locations(
            points=points,
            interval_seconds=frames_interval
        )
        
        # Calculate path statistics
        path_stats = location_helper.calculate_path_stats(interpolated_points)
        
        # Get video frames at interpolated timestamps
        frames = video_helper.split_video_to_frames(
            video_bytes=video_bytes,
            max_frames=len(interpolated_points),
            frame_interval=frames_interval
        )
        
        # Combine frames with location data
        result = []
        for point, frame in zip(interpolated_points, frames):
            result.append({
                **point,
                'frame': frame
            })
        
        return jsonify({
            'metadata': metadata,
            'path_stats': path_stats,
            'points': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)