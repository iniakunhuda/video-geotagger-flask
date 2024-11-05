import io
import mimetypes
import json
from exif import Flash, Image as ExifImage
from PIL import Image as PILImage
from fractions import Fraction
from typing import Union, Dict, Any, Optional, List

class ExifHelper:
    def __init__(self):
        self.gps_coordinate_refs = {'N': 1, 'S': -1, 'E': 1, 'W': -1}

    def make_serializable(self, value: Any) -> Any:
        """Convert EXIF data types to JSON serializable formats."""
        if isinstance(value, bytes):
            return value.decode(errors='ignore')
        elif isinstance(value, (str, int, float)):
            return value
        elif isinstance(value, (tuple, list)):
            return [self.make_serializable(v) for v in value]
        elif isinstance(value, dict):
            return {str(k): self.make_serializable(v) for k, v in value.items()}
        elif hasattr(value, 'numerator') and hasattr(value, 'denominator'):
            return float(value.numerator) / float(value.denominator)
        elif isinstance(value, Flash):
            return {
                'flash_fired': value.flash_fired,
                'flash_return': value.flash_return.name,
                'flash_mode': value.flash_mode.name,
                'flash_function_not_present': value.flash_function_not_present,
                'red_eye_reduction_supported': value.red_eye_reduction_supported,
                'reserved': value.reserved
            }
        return str(value)

    def _get_color_model(self, color_space: Optional[int]) -> str:
        """Determine color model from color space value."""
        color_models = {
            1: "sRGB",
            2: "Adobe RGB",
            65535: "Uncalibrated"
        }
        return color_models.get(color_space, "RGB")

    def format_return_exif(self, exif_data: Dict[str, Any], file_name: str, 
                         file_type: str, mime_type: str) -> Dict[str, Any]:
        """Format EXIF data into a standardized structure."""
        color_model = self._get_color_model(exif_data.get("color_space"))
        
        return {
            "altitude": exif_data.get("gps_altitude"),
            "latitude": exif_data.get("gps_latitude"),
            "longitude": exif_data.get("gps_longitude"),
            "name": file_name,
            "file_size": exif_data.get("jpeg_interchange_format_length"),
            "file_type": file_type,
            "mime_type": mime_type,
            "image_size": f"{exif_data.get('pixel_x_dimension', 0)} x {exif_data.get('pixel_y_dimension', 0)}",
            "color_space": exif_data.get("color_space"),
            "color_model": color_model,
            "created_at": exif_data.get("datetime_original"),
            "camera": {
                "make": exif_data.get("make"),
                "model": exif_data.get("model"),
                "lens": exif_data.get("lens_model"),
                "focal_length": exif_data.get("focal_length"),
                "aperture": exif_data.get("f_number"),
                "exposure": exif_data.get("exposure_time"),
                "iso": exif_data.get("photographic_sensitivity"),
                "flash": exif_data.get("flash"),
            }
        }

    def get_exif_data(self, image_input: Union[bytes, str]) -> Optional[Dict[str, Any]]:
        """Extract EXIF data from an image file or bytes."""
        try:
            # Handle both file paths and bytes
            if isinstance(image_input, bytes):
                img = PILImage.open(io.BytesIO(image_input))
                file_name = "Image from Bytes"
                image = ExifImage(image_input)
            else:
                img = PILImage.open(image_input)
                file_name = img.filename
                with open(image_input, 'rb') as f:
                    image = ExifImage(f)

            if not image.has_exif:
                return None

            file_type = img.format
            mime_type = mimetypes.types_map.get(f".{file_type.lower()}", "image/jpeg")
            
            exif_data = {}
            for tag in image.list_all():
                if tag not in ('gps_latitude_ref', 'gps_longitude_ref'):
                    exif_data[tag] = self.make_serializable(image.get(tag))
            
            return self.format_return_exif(exif_data, file_name, file_type, mime_type)
            
        except Exception as e:
            raise Exception(f"Error processing EXIF data: {str(e)}")

    def _convert_to_degrees(self, value: float) -> List[float]:
        """Convert decimal degrees to degrees, minutes, seconds."""
        degrees = int(value)
        minutes = int((value - degrees) * 60)
        seconds = ((value - degrees) * 60 - minutes) * 60
        return [float(degrees), float(minutes), float(seconds)]

    def convert_to_rational(self, number: Union[float, List[float], None]) -> Optional[Union[Fraction, List[Fraction]]]:
        """Convert decimal numbers to rational numbers for EXIF."""
        if number is None:
            return None
        
        try:
            if isinstance(number, (list, tuple)):
                return [Fraction(str(float(n))).limit_denominator(10000) for n in number]
            return Fraction(str(float(number))).limit_denominator(10000)
        except Exception as e:
            raise ValueError(f"Error converting {number} to rational: {str(e)}")

    def write_exif_data(self, image_path: str, metadata: Dict[str, str]) -> Dict[str, Any]:
        try:
            # Parse the JSON string from metadata
            gps_data = json.loads(metadata['metadata'])

            # Open image in binary mode
            exif_image = ExifImage(image_path)

            # Set latitude
            if 'gps_latitude' in gps_data:
                lat_deg = Fraction(str(float(gps_data['gps_latitude'][0]))).limit_denominator(10000)
                lat_min = Fraction(str(float(gps_data['gps_latitude'][1]))).limit_denominator(10000)
                lat_sec = Fraction(str(float(gps_data['gps_latitude'][2]))).limit_denominator(10000)
                
                exif_image.gps_latitude = (lat_deg, lat_min, lat_sec)
                exif_image.gps_latitude_ref = gps_data['gps_latitude_ref']

            # Set longitude
            if 'gps_longitude' in gps_data:
                lon_deg = Fraction(str(float(gps_data['gps_longitude'][0]))).limit_denominator(10000)
                lon_min = Fraction(str(float(gps_data['gps_longitude'][1]))).limit_denominator(10000)
                lon_sec = Fraction(str(float(gps_data['gps_longitude'][2]))).limit_denominator(10000)
                
                exif_image.gps_longitude = (lon_deg, lon_min, lon_sec)
                exif_image.gps_longitude_ref = gps_data['gps_longitude_ref']

            # Set altitude
            if 'gps_altitude' in gps_data:
                altitude = Fraction(str(float(gps_data['gps_altitude']))).limit_denominator(10000)
                exif_image.gps_altitude = altitude
                # Convert altitude reference string to binary value
                altitude_ref = 0 if gps_data.get('gps_altitude_ref', '').upper() == 'ABOVE_SEA_LEVEL' else 1
                exif_image.gps_altitude_ref = altitude_ref

            # Write the modified image
            output_path = "output_with_exif.jpg"
            with open(output_path, 'wb') as new_image_file:
                new_image_file.write(exif_image.get_file())

            # Return the processed GPS data for verification
            return {
                'gps_latitude': exif_image.gps_latitude,
                'gps_latitude_ref': exif_image.gps_latitude_ref,
                'gps_longitude': exif_image.gps_longitude,
                'gps_longitude_ref': exif_image.gps_longitude_ref,
                'gps_altitude': exif_image.gps_altitude,
                'gps_altitude_ref': exif_image.gps_altitude_ref
            }

        except Exception as e:
            raise Exception(f"Error writing EXIF data: {str(e)}")