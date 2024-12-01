import cv2
import numpy as np
import io
from typing import List, Optional, Dict, Tuple
import base64
import os
import pandas as pd
from datetime import datetime
from flask import request, jsonify
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
import piexif.helper
from pathlib import Path

"""
Convert csv + video to frame
Input:
    - CSV file
    - Video
Output:
    - Frame every x seconds
        - EXIF data (latitude, longitude)
"""

class GeotaggerHelper:
    def __init__(self, csv_path: str, video_path: str, output_dir: str, frame_interval: int = 1):
        """
        Initialize the GeotaggerHelper with paths to CSV and video files
        
        Args:
            csv_path: Path to the CSV file containing telemetry data
            video_path: Path to the video file
            output_dir: Base directory for saving frames
            frame_interval: Interval in seconds between frame captures
        """
        self.csv_path = csv_path
        self.video_path = video_path
        self.output_dir = output_dir
        self.frame_interval = frame_interval
        self.telemetry_data = None
        self.video_capture = None

    def create_output_directory(self, timestamp: datetime) -> str:
        """Create and return path to date-based output directory"""
        date_dir = os.path.join(
            self.output_dir,
            f"{timestamp.year}-{timestamp.month:02d}-{timestamp.day:02d}"
        )
        os.makedirs(date_dir, exist_ok=True)
        return date_dir

    def convert_to_degree_minutes_seconds(self, decimal_degrees: float, is_latitude: bool) -> tuple:
        """Convert decimal degrees to degrees, minutes, seconds format"""
        direction = 'N' if decimal_degrees >= 0 and is_latitude else 'S' if is_latitude else 'E' if decimal_degrees >= 0 else 'W'
        decimal_degrees = abs(decimal_degrees)
        degrees = int(decimal_degrees)
        minutes = int((decimal_degrees - degrees) * 60)
        seconds = ((decimal_degrees - degrees) * 60 - minutes) * 60
        return ((degrees, 1), (minutes, 1), (int(seconds * 100), 100)), direction

    def create_exif_bytes(self, telemetry: Dict) -> bytes:
        """Create EXIF data bytes from telemetry data"""
        # Create EXIF dictionary
        exif_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "1st": {},
            "thumbnail": None
        }

        # Convert latitude and longitude to EXIF format
        lat_dms, lat_ref = self.convert_to_degree_minutes_seconds(float(telemetry['latitude']), True)
        lon_dms, lon_ref = self.convert_to_degree_minutes_seconds(float(telemetry['longitude']), False)

        # Set GPS Info
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = lat_ref
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = lat_dms
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = lon_ref
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = lon_dms
        exif_dict["GPS"][piexif.GPSIFD.GPSAltitude] = (int(float(telemetry['altitude']) * 100), 100)

        # Add custom telemetry data to EXIF UserComment
        # user_comment = {
        #     'compass_heading': telemetry['compass_heading'],
        #     'pitch': telemetry['pitch'],
        #     'roll': telemetry['roll'],
        #     'speed': telemetry['speed'],
        #     'battery_percent': telemetry['battery_percent'],
        #     'gimbal_heading': telemetry['gimbal_heading'],
        #     'gimbal_pitch': telemetry['gimbal_pitch'],
        #     'gimbal_roll': telemetry['gimbal_roll']
        # }
        # user_comment_str = piexif.helper.UserComment.dump(str(user_comment))
        # exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment_str

        return piexif.dump(exif_dict)

    def save_frame_with_exif(self, frame: np.ndarray, telemetry: Dict, timestamp: datetime) -> str:
        """Save frame as JPEG with EXIF data"""
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create PIL Image
        image = Image.fromarray(frame_rgb)
        
        # Create output directory and filename
        output_dir = self.create_output_directory(timestamp)
        filename = f"frame_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        output_path = os.path.join(output_dir, filename)
        
        # Create EXIF data
        exif_bytes = self.create_exif_bytes(telemetry)
        
        # Save image with EXIF data
        image.save(output_path, "jpeg", exif=exif_bytes)
        
        return output_path

    def load_telemetry_data(self) -> None:
        """Load and process the CSV telemetry data"""
        try:
            df = pd.read_csv(self.csv_path)
            df.columns = df.columns.str.strip()
            df['timestamp'] = pd.to_datetime(df['datetime(utc)'])
            self.telemetry_data = df
        except Exception as e:
            raise Exception(f"Failed to load telemetry data: {str(e)}")
            
    def load_video(self) -> None:
        """Load the video file"""
        self.video_capture = cv2.VideoCapture(self.video_path)
        if not self.video_capture.isOpened():
            raise Exception("Failed to open video file")
            
    def get_telemetry_at_timestamp(self, timestamp: datetime) -> Dict:
        """Get telemetry data closest to the given timestamp"""
        if self.telemetry_data is None:
            raise Exception("Telemetry data not loaded")
            
        closest_row = self.telemetry_data.iloc[(self.telemetry_data['timestamp'] - timestamp).abs().argsort()[0]]
        return {
            'latitude': closest_row['latitude'],
            'longitude': closest_row['longitude'],
            'altitude': closest_row['altitude(feet)']
            # 'height_above_takeoff': closest_row['height_above_takeoff(feet)'],
            # 'speed': closest_row['speed(mph)'],
            # 'compass_heading': closest_row['compass_heading(degrees)'].strip(),
            # 'pitch': closest_row['pitch(degrees)'].strip(),
            # 'roll': closest_row['roll(degrees)'].strip(),
            # 'battery_percent': closest_row['battery_percent'],
            # 'voltage': closest_row['voltage(v)'],
            # 'satellites': closest_row['satellites'],
            # 'gps_level': closest_row['gpslevel'],
            # 'gimbal_heading': closest_row['gimbal_heading(degrees)'],
            # 'gimbal_pitch': closest_row['gimbal_pitch(degrees)'],
            # 'gimbal_roll': closest_row['gimbal_roll(degrees)']
        }

    def process_video(self) -> List[Dict]:
        """Process video and save frames with EXIF data"""
        if self.video_capture is None or self.telemetry_data is None:
            raise Exception("Video and telemetry data must be loaded first")
            
        saved_frames = []
        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        
        # Get all unique timestamps from CSV
        csv_timestamps = self.telemetry_data['timestamp'].unique()
        print(f"Total unique timestamps in CSV: {len(csv_timestamps)}")
        
        # Calculate video duration
        total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = total_frames / fps
        print(f"Video duration: {video_duration} seconds")
        
        # Calculate frame interval based on CSV frequency
        csv_duration = (csv_timestamps[-1] - csv_timestamps[0]).total_seconds()
        ideal_interval = csv_duration / len(csv_timestamps)
        frame_interval = int(ideal_interval * fps)
        print(f"Calculated frame interval: {frame_interval} frames")
        
        video_start_time = csv_timestamps[0]
        
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                break
                
            # Get current video position in seconds
            current_pos_ms = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
            current_pos_sec = current_pos_ms / 1000.0
            
            # Find closest CSV timestamp
            current_timestamp = video_start_time + pd.Timedelta(seconds=current_pos_sec)
            
            # Process frame if it's close to a CSV timestamp
            closest_csv_time = min(csv_timestamps, key=lambda x: abs((x - current_timestamp).total_seconds()))
            time_diff = abs((closest_csv_time - current_timestamp).total_seconds())
            
            if time_diff < 0.1:  # Within 100ms of a CSV timestamp
                print(f"Processing frame at {current_timestamp}")
                telemetry = self.get_telemetry_at_timestamp(closest_csv_time)
                
                # Save frame with EXIF data
                saved_path = self.save_frame_with_exif(frame, telemetry, closest_csv_time)
                
                frame_info = {
                    'timestamp': closest_csv_time.isoformat(),
                    'path': saved_path,
                    'telemetry': telemetry
                }
                saved_frames.append(frame_info)
                
            frame_count += 1
            
        print(f"Total frames processed: {frame_count}")
        print(f"Total frames saved: {len(saved_frames)}")
        return saved_frames

    def __del__(self):
        """Cleanup resources"""
        if self.video_capture is not None:
            self.video_capture.release()