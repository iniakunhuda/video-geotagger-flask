from typing import List, Dict, Any
import numpy as np
from geopy.distance import geodesic

class LocationHelper:
    def validate_timestamps(self, points: List[Dict[str, Any]]) -> bool:
        """
        Validate that timestamps are valid numbers
        """
        try:
            for point in points:
                # Check if timestamp can be converted to float
                float(point.get('timestamp', 0))
            return True
        except (ValueError, TypeError):
            return False

    def interpolate_locations(self, points: List[Dict[str, Any]], interval_seconds: int) -> List[Dict[str, Any]]:
        """
        Interpolate locations between points at specified intervals.
        
        Args:
            points (List[Dict]): List of points with timestamp, lat, lon
            interval_seconds (int): Interval in seconds between interpolated points
            
        Returns:
            List[Dict]: Interpolated points with timestamp, lat, lon
        """
        if len(points) < 2:
            return points

        interpolated = []
        
        # Convert all timestamps to float
        for point in points:
            point['timestamp'] = float(point['timestamp'])
        
        # Sort points by timestamp
        points = sorted(points, key=lambda x: x['timestamp'])
        
        # Process each pair of consecutive points
        for i in range(len(points) - 1):
            start_point = points[i]
            end_point = points[i + 1]
            
            start_time = start_point['timestamp']
            end_time = end_point['timestamp']
            
            # Calculate number of intervals between these points
            time_diff = end_time - start_time
            num_intervals = max(1, int(time_diff / interval_seconds))
            
            # Create timestamps for interpolation
            timestamps = np.linspace(start_time, end_time, num_intervals + 1)
            
            # Interpolate lat/lon for each timestamp
            for t in timestamps[:-1]:  # Exclude last point except for final segment
                progress = (t - start_time) / (end_time - start_time)
                
                # Linear interpolation
                lat = start_point['lat'] + progress * (end_point['lat'] - start_point['lat'])
                lon = start_point['lon'] + progress * (end_point['lon'] - start_point['lon'])
                
                interpolated.append({
                    'timestamp': float(t),
                    'lat': lat,
                    'lon': lon
                })
        
        # Add the last point
        interpolated.append({
            'timestamp': float(points[-1]['timestamp']),
            'lat': points[-1]['lat'],
            'lon': points[-1]['lon']
        })
        
        return interpolated

    def calculate_path_stats(self, points: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate statistics for a path.
        
        Args:
            points (List[Dict]): List of points with timestamp, lat, lon
            
        Returns:
            Dict[str, float]: Statistics including distance, duration, speed
        """
        if len(points) < 2:
            return {
                'total_distance': 0,
                'duration': 0,
                'average_speed': 0,
                'point_count': len(points)
            }
        
        total_distance = 0
        
        # Calculate total distance
        for i in range(len(points) - 1):
            point1 = (points[i]['lat'], points[i]['lon'])
            point2 = (points[i + 1]['lat'], points[i + 1]['lon'])
            distance = geodesic(point1, point2).meters
            total_distance += distance
        
        # Calculate duration
        duration = points[-1]['timestamp'] - points[0]['timestamp']
        
        # Calculate average speed
        average_speed = total_distance / duration if duration > 0 else 0
        
        return {
            'total_distance': total_distance,
            'duration': duration,
            'average_speed': average_speed,
            'point_count': len(points)
        }