import numpy as np
from scipy.interpolate import CubicSpline
from typing import List, Dict, Union
from datetime import datetime, timedelta

class LocationHelper:
    def __init__(self):
        self.interpolation_method = 'cubic'  # can be 'cubic' or 'linear'
        
    def _parse_timestamp(self, timestamp: str) -> int:
        """Convert timestamp string (MMSS) to seconds."""
        if len(timestamp) != 4:
            raise ValueError(f"Invalid timestamp format: {timestamp}. Expected format: 'MMSS'")
        
        minutes = int(timestamp[:2])
        seconds = int(timestamp[2:])
        return minutes * 60 + seconds
        
    def _format_timestamp(self, seconds: int) -> str:
        """Convert seconds to timestamp string (MMSS)."""
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02d}{remaining_seconds:02d}"
    
    def interpolate_locations(self, 
                            points: List[Dict[str, Union[str, float]]], 
                            interval_seconds: int = 5) -> List[Dict[str, Union[str, float]]]:
        """
        Interpolate GPS coordinates between given timestamps.
        
        Args:
            points: List of dictionaries containing timestamp, lat, and lon
            interval_seconds: Interval in seconds between interpolated points
            
        Returns:
            List of dictionaries with interpolated coordinates
        """
        try:
            # Sort points by timestamp
            sorted_points = sorted(points, key=lambda x: self._parse_timestamp(x['timestamp']))
            
            # Extract timestamps, latitudes, and longitudes
            timestamps = np.array([self._parse_timestamp(p['timestamp']) for p in sorted_points])
            lats = np.array([float(p['lat']) for p in sorted_points])
            lons = np.array([float(p['lon']) for p in sorted_points])
            
            # Create interpolation functions
            cs_lat = CubicSpline(timestamps, lats)
            cs_lon = CubicSpline(timestamps, lons)
            
            # Generate timestamps for interpolation
            start_time = timestamps[0]
            end_time = timestamps[-1]
            interp_timestamps = np.arange(start_time, end_time + interval_seconds, interval_seconds)
            
            # Interpolate coordinates
            interp_lats = cs_lat(interp_timestamps)
            interp_lons = cs_lon(interp_timestamps)
            
            # Format results
            results = []
            for t, lat, lon in zip(interp_timestamps, interp_lats, interp_lons):
                results.append({
                    'timestamp': self._format_timestamp(int(t)),
                    'lat': round(float(lat), 6),
                    'lon': round(float(lon), 6)
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error interpolating locations: {str(e)}")
            
    def validate_timestamps(self, points: List[Dict[str, Union[str, float]]]) -> bool:
        """Validate timestamp format and sequence."""
        try:
            for point in points:
                timestamp = point['timestamp']
                if not (len(timestamp) == 4 and timestamp.isdigit()):
                    return False
                    
                minutes = int(timestamp[:2])
                seconds = int(timestamp[2:])
                
                if minutes > 59 or seconds > 59:
                    return False
                    
            return True
        except:
            return False
            
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
        
    def calculate_path_stats(self, points: List[Dict[str, Union[str, float]]]) -> Dict[str, float]:
        """Calculate statistics for the interpolated path."""
        total_distance = 0
        speeds = []
        
        for i in range(1, len(points)):
            lat1 = points[i-1]['lat']
            lon1 = points[i-1]['lon']
            lat2 = points[i]['lat']
            lon2 = points[i]['lon']
            
            # Calculate distance
            distance = self.calculate_distance(lat1, lon1, lat2, lon2)
            total_distance += distance
            
            # Calculate speed (km/h)
            time_diff = (self._parse_timestamp(points[i]['timestamp']) - 
                        self._parse_timestamp(points[i-1]['timestamp'])) / 3600
            if time_diff > 0:
                speed = distance / time_diff
                speeds.append(speed)
        
        return {
            'total_distance_km': round(total_distance, 2),
            'average_speed_kmh': round(np.mean(speeds), 2) if speeds else 0,
            'max_speed_kmh': round(np.max(speeds), 2) if speeds else 0
        }