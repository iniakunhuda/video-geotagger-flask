from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import io
import json
import tempfile
from datetime import datetime
import os

from helpers.ExifHelper import ExifHelper
from helpers.LocationHelper import LocationHelper
from helpers.VideoHelper import VideoHelper
from helpers.GeotaggerHelper import GeotaggerHelper
from helpers.GeotaggerHelperInterval import GeotaggerHelperInterval

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
        frames_interval = request.form.get('frames_interval', '1')
        try:
            frames_interval = int(frames_interval)
            if frames_interval <= 0:
                return jsonify({'error': 'frames_interval must be positive'}), 400
        except ValueError:
            return jsonify({'error': 'frames_interval must be a number'}), 400
            
        # Get and validate markers data
        markers_data = request.form.get('markers')
        if not markers_data:
            return jsonify({'error': 'markers data is required'}), 400
            
        try:
            markers = json.loads(markers_data)
            if not isinstance(markers, list):
                return jsonify({'error': 'markers data must be a list'}), 400
                
            # Convert markers to points format
            points = []
            for marker in markers:
                if not all(k in marker for k in ('timestamp', 'lat', 'lng')):
                    return jsonify({'error': 'Invalid marker format. Each marker must have timestamp, lat, and lng'}), 400
                points.append({
                    'timestamp': float(marker['timestamp']),
                    'lat': float(marker['lat']),
                    'lon': float(marker['lng'])  # Note: convert lng to lon
                })
                    
            # Sort points by timestamp
            points.sort(key=lambda x: x['timestamp'])
                    
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON format in markers data'}), 400
            
        # Create helpers
        video_helper = VideoHelper()
        location_helper = LocationHelper()
        
        # Get video metadata
        video_bytes = video_file.read()
        metadata = video_helper.get_video_metadata(video_bytes)
        
        if not metadata:
            return jsonify({'error': 'Failed to read video metadata'}), 400
            
        # Check video duration (2 min limit)
        if metadata.get('duration', 0) > 120:  # 120 seconds = 2 minutes
            return jsonify({'error': 'Video duration exceeds 2 minutes limit'}), 400
            
        # Interpolate locations
        try:
            interpolated_points = location_helper.interpolate_locations(
                points=points,
                interval_seconds=frames_interval
            )
        except Exception as e:
            return jsonify({'error': f'Error interpolating locations: {str(e)}'}), 400
        
        # Calculate path statistics
        path_stats = location_helper.calculate_path_stats(interpolated_points)
        
        # Get frames at interpolated timestamps
        frames = video_helper.extract_frames_at_timestamps(
            video_bytes=video_bytes,
            timestamps=[point['timestamp'] for point in interpolated_points]
        )
        
        # Combine frames with location data
        result = []
        for point, frame in zip(interpolated_points, frames):
            if frame:  # Only include if frame was successfully extracted
                result.append({
                    'timestamp': point['timestamp'],
                    'lat': point['lat'],
                    'lng': point['lon'],  # Convert back to lng for frontend
                    'frame': frame
                })
        
        return jsonify({
            'metadata': metadata,
            'path_stats': path_stats,
            'points': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
    
@app.route('/interpolate-path-v2', methods=['POST', 'OPTIONS'])
def interpolate_path_v2():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        # Validate video file
        if 'video' not in request.files:
            return jsonify({'error': 'No video file found in the request'}), 400
            
        video_file = request.files['video']
        
        # Get and validate markers data
        markers_data = request.form.get('markers')
        if not markers_data:
            return jsonify({'error': 'markers data is required'}), 400
            
        try:
            markers = json.loads(markers_data)
            if not isinstance(markers, list):
                return jsonify({'error': 'markers data must be a list'}), 400
                
            # Validate marker structure
            for marker in markers:
                if not all(k in marker for k in ('timestamp', 'lat', 'lng')):
                    return jsonify({'error': 'Invalid marker format. Each marker must have timestamp, lat, and lng'}), 400
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON format in markers data'}), 400
            
        # Create helpers
        video_helper = VideoHelper()
        
        # Get video metadata and frames
        video_bytes = video_file.read()
        metadata = video_helper.get_video_metadata(video_bytes)
        
        if not metadata:
            return jsonify({'error': 'Failed to read video metadata'}), 400
            
        # Extract frames at marker timestamps
        frames = video_helper.extract_frames_at_timestamps(
            video_bytes=video_bytes,
            timestamps=[marker['timestamp'] for marker in markers]
        )
        
        # Combine frames with marker data
        result = []
        for marker, frame in zip(markers, frames):
            if frame:  # Only include if frame was successfully extracted
                result.append({
                    'timestamp': marker['timestamp'],
                    'lat': marker['lat'],
                    'lng': marker['lng'],
                    'frame': frame
                })
        
        return jsonify({
            'metadata': metadata,
            'points': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/geotagger-video-test', methods=['POST', 'OPTIONS'])
def geotagger_video_test():
    # Open json result2.json
    try:
        with open('result-all.json', 'r') as file:
            data = json.load(file)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/geotagger-video', methods=['POST', 'OPTIONS'])
def geotagger_video():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        if 'video' not in request.files or 'csv' not in request.files:
            return jsonify({'error': 'Missing video or CSV file'}), 400
            
        video_file = request.files['video']
        csv_file = request.files['csv']
        
        # Get output directory from request or use default
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, 'drone_frames')
        # output_dir = request.form.get('output_dir', 'drone_frames')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as video_tmp:
            video_file.save(video_tmp.name)
            video_path = video_tmp.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as csv_tmp:
            csv_file.save(csv_tmp.name)
            csv_path = csv_tmp.name
            
        try:
            helper = GeotaggerHelper(csv_path, video_path, output_dir)
            helper.load_telemetry_data()
            helper.load_video()
            saved_frames = helper.process_video_all()
            
            return jsonify({
                'status': 'success',
                'saved_frames': saved_frames
            })
            
        finally:
            os.unlink(video_path)
            os.unlink(csv_path)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/geotagger-video-interval', methods=['POST', 'OPTIONS'])
def geotagger_video_interval():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        if 'video' not in request.files or 'csv' not in request.files:
            return jsonify({'error': 'Missing video or CSV file'}), 400
            
        video_file = request.files['video']
        csv_file = request.files['csv']
        
        # Get frame_interval from the request form
        frame_interval = float(request.form.get('frame_interval', 1))
        
        # Get output directory from request or use default
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, 'drone_frames')
        # output_dir = request.form.get('output_dir', 'drone_frames')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as video_tmp:
            video_file.save(video_tmp.name)
            video_path = video_tmp.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as csv_tmp:
            csv_file.save(csv_tmp.name)
            csv_path = csv_tmp.name
            
        try:
            helper = GeotaggerHelperInterval(csv_path, video_path, output_dir, frame_interval)
            helper.load_telemetry_data()
            helper.load_video()
            saved_frames = helper.process_video()
            
            return jsonify({
                'status': 'success',
                'saved_frames': saved_frames
            })
            
        finally:
            os.unlink(video_path)
            os.unlink(csv_path)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Route to serve images from drone_frames directory
@app.route('/drone_frames/<path:filename>')
def serve_drone_frames(filename):
    # Get the absolute path to the drone_frames directory
    drone_frames_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drone_frames')
    
    # Extract the directory path from the filename
    directory = os.path.dirname(filename)
    base_filename = os.path.basename(filename)
    
    # Construct the full directory path
    full_directory = os.path.join(drone_frames_dir, directory)
    
    return send_from_directory(full_directory, base_filename)
    
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)