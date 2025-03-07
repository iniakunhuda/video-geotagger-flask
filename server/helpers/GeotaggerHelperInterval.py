from helpers.GeotaggerHelper import GeotaggerHelper

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

class GeotaggerHelperInterval(GeotaggerHelper):
    def __init__(self, csv_path: str, video_path: str, output_dir: str, frame_interval: float = 1):
        """
        Initialize the GeotaggerHelperInterval with paths to CSV and video files
        
        Args:
            csv_path: Path to the CSV file containing telemetry data
            video_path: Path to the video file
            output_dir: Base directory for saving frames
            frame_interval: Interval in seconds between frame captures
        """
        super().__init__(csv_path, video_path, output_dir, frame_interval)
        
    def process_video(self) -> List[Dict]:
        """Process video and save frames at specified intervals with EXIF data"""
        if self.video_capture is None or self.telemetry_data is None:
            raise Exception("Video and telemetry data must be loaded first")
            
        saved_frames = []
        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        
        # Get video duration and start time
        total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = total_frames / fps
        video_start_time = self.telemetry_data['timestamp'].iloc[0]
        
        print(f"Video duration: {video_duration} seconds")
        print(f"Total frames: {total_frames}")
        print(f"Frame interval: {self.frame_interval} seconds")
        
        # Calculate frame step based on FPS and interval
        frame_step = int(fps * self.frame_interval)
        if frame_step < 1:
            frame_step = 1
            
        print(f"Frame step: {frame_step} frames")
        
        current_frame = 0
        
        while current_frame < total_frames:
            # Set frame position
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            
            # Read frame
            ret, frame = self.video_capture.read()
            if not ret:
                break
                
            # Calculate current timestamp
            current_pos_sec = current_frame / fps
            current_timestamp = video_start_time + pd.Timedelta(seconds=current_pos_sec)
            
            # Get telemetry at timestamp
            telemetry = self.get_telemetry_at_timestamp(current_timestamp)
            
            # Save frame with EXIF data
            saved_path = self.save_frame_with_exif(frame, telemetry, current_timestamp)
            
            frame_info = {
                'timestamp': current_timestamp.isoformat(),
                'path': saved_path,
                'telemetry': telemetry,
                'frame_number': current_frame
            }
            saved_frames.append(frame_info)
            
            # Move to next frame based on interval
            current_frame += frame_step
            
            if len(saved_frames) % 10 == 0:
                print(f"Processed {len(saved_frames)} frames")
        
        print(f"Total frames processed: {len(saved_frames)}")
        return saved_frames