import cv2
import numpy as np
import io
from typing import List, Optional
import base64
import tempfile
import os

class VideoHelper:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv']
        
    def _bytes_to_video(self, video_bytes: bytes) -> Optional[cv2.VideoCapture]:
        """Convert bytes to VideoCapture object."""
        try:
            # Create a temporary file to store the video
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(video_bytes)
                temp_path = temp_file.name
            
            # Create video capture object from the temporary file
            video = cv2.VideoCapture(temp_path)
            
            # Delete the temporary file
            os.unlink(temp_path)
            
            if not video.isOpened():
                return None
                
            return video
        except Exception as e:
            print(f"Error converting bytes to video: {str(e)}")
            return None
    
    def _frame_to_base64(self, frame: np.ndarray) -> Optional[str]:
        """Convert frame to base64 string with proper image data URI."""
        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame_rgb, [
                cv2.IMWRITE_JPEG_QUALITY, 85,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ])
            
            # Convert to base64 and add data URI prefix
            base64_data = base64.b64encode(buffer).decode('utf-8')
            base64_frame = f"data:image/jpeg;base64,{base64_data}"
            
            return base64_frame
        except Exception as e:
            print(f"Error converting frame to base64: {str(e)}")
            return None

    def split_video_to_frames(self, video_bytes: bytes, max_frames: int = 30, frame_interval: int = 1) -> List[str]:
        """
        Split video into frames and return them as base64 encoded strings.
        
        Args:
            video_bytes (bytes): Video file in bytes
            max_frames (int): Maximum number of frames to extract
            frame_interval (int): Interval between frames to extract
            
        Returns:
            List[str]: List of base64 encoded frames with data URI prefix
        """
        try:
            # Convert bytes to video
            video = self._bytes_to_video(video_bytes)
            if video is None:
                return []
            
            # Get total frame count
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate optimal frame interval if total frames is less than desired
            if total_frames < max_frames:
                frame_interval = 1
            else:
                # Adjust frame interval to get better distribution
                frame_interval = max(1, total_frames // max_frames)
            
            frames = []
            frame_count = 0
            
            while frame_count < total_frames:
                # Set frame position
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
                
                # Read frame
                success, frame = video.read()
                
                if not success:
                    break
                
                # Resize frame if it's too large
                height, width = frame.shape[:2]
                if width > 1280:  # Max width threshold
                    scale = 1280 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                
                # Convert frame to base64
                base64_frame = self._frame_to_base64(frame)
                
                if base64_frame:
                    frames.append(base64_frame)
                    
                    # Check if we've reached max frames
                    if len(frames) >= max_frames:
                        break
                
                # Move to next frame position
                frame_count += frame_interval
            
            # Release video capture
            video.release()
            
            return frames
            
        except Exception as e:
            print(f"Error splitting video to frames: {str(e)}")
            return []

    def get_video_metadata(self, video_bytes: bytes) -> dict:
        """
        Get video metadata.
        
        Returns:
            dict: Dictionary containing video metadata
        """
        try:
            video = self._bytes_to_video(video_bytes)
            if video is None:
                return {}
            
            # Get video properties
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Release video capture
            video.release()
            
            return {
                'fps': round(fps, 2),
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': round(duration, 2),
                'duration_formatted': self._format_duration(duration),
                'codec': self._get_codec_info(video_bytes)
            }
            
        except Exception as e:
            print(f"Error getting video metadata: {str(e)}")
            return {}
            
    def _get_codec_info(self, video_bytes: bytes) -> str:
        """Get video codec information."""
        try:
            video = self._bytes_to_video(video_bytes)
            if video is None:
                return "unknown"
            
            # Get the codec value
            fourcc = int(video.get(cv2.CAP_PROP_FOURCC))
            codec = chr(fourcc & 0xFF) + chr((fourcc >> 8) & 0xFF) + chr((fourcc >> 16) & 0xFF) + chr((fourcc >> 24) & 0xFF)
            
            video.release()
            return codec.strip()
        except:
            return "unknown"
            
    def _format_duration(self, duration: float) -> str:
        """Format duration in seconds to HH:MM:SS format."""
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
        
    def extract_frames_at_timestamps(self, video_bytes: bytes, timestamps: List[float]) -> List[str]:
        """
        Extract frames at specific timestamps from video.
        
        Args:
            video_bytes (bytes): Video file in bytes
            timestamps (List[float]): List of timestamps in seconds
            
        Returns:
            List[str]: List of base64 encoded frames with data URI prefix
        """
        try:
            # Convert bytes to video
            video = self._bytes_to_video(video_bytes)
            if video is None:
                return []
            
            # Get video properties
            fps = video.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                return []
                
            frames = []
            
            for timestamp in timestamps:
                # Convert timestamp to frame number
                frame_number = int(timestamp * fps)
                
                # Set frame position
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                
                # Read frame
                success, frame = video.read()
                
                if not success:
                    frames.append(None)
                    continue
                
                # Resize frame if it's too large
                height, width = frame.shape[:2]
                if width > 1280:  # Max width threshold
                    scale = 1280 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                
                # Convert frame to base64
                base64_frame = self._frame_to_base64(frame)
                frames.append(base64_frame)
            
            # Release video capture
            video.release()
            
            return frames
            
        except Exception as e:
            print(f"Error extracting frames at timestamps: {str(e)}")
            return []