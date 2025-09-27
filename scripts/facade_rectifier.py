"""
Facade Rectification Pipeline
Converts perspective photos of building facades into orthographic projections
"""

import cv2
import numpy as np
import os
from pathlib import Path

class FacadeRectifier:
    def __init__(self, output_size=(512, 512)):
        self.output_size = output_size
        self.corners = []
        self.current_image = None
        self.original_image = None
        
    def mouse_callback(self, event, x, y, flags, param):
        """Mouse callback for selecting facade corners"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.corners) < 4:
                self.corners.append((x, y))
                # Draw point on image
                cv2.circle(self.current_image, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(self.current_image, str(len(self.corners)), 
                           (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                print(f"Corner {len(self.corners)}: ({x}, {y})")
                
                if len(self.corners) == 4:
                    print("All 4 corners selected! Press 'r' to rectify or 'c' to clear")
                    
    def load_image(self, image_path):
        """Load and prepare image for rectification"""
        self.original_image = cv2.imread(str(image_path))
        if self.original_image is None:
            raise ValueError(f"Could not load image: {image_path}")
            
        # Resize for display if too large
        height, width = self.original_image.shape[:2]
        if width > 1200 or height > 800:
            scale = min(1200/width, 800/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            self.display_image = cv2.resize(self.original_image, (new_width, new_height))
            self.scale_factor = scale
        else:
            self.display_image = self.original_image.copy()
            self.scale_factor = 1.0
            
        self.current_image = self.display_image.copy()
        return True
        
    def select_corners_interactive(self):
        """Interactive corner selection"""
        self.corners = []
        
        print("Click on the 4 corners of the facade in this order:")
        print("1. Top-left")
        print("2. Top-right") 
        print("3. Bottom-right")
        print("4. Bottom-left")
        print("Press 'c' to clear corners, 'r' to rectify, 'q' to quit")
        
        cv2.namedWindow('Select Facade Corners', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('Select Facade Corners', self.mouse_callback)
        
        while True:
            cv2.imshow('Select Facade Corners', self.current_image)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                cv2.destroyAllWindows()
                return False
            elif key == ord('c'):
                # Clear corners and reset image
                self.corners = []
                self.current_image = self.display_image.copy()
                print("Corners cleared")
            elif key == ord('r') and len(self.corners) == 4:
                cv2.destroyAllWindows()
                return True
                
    def rectify_facade(self):
        """Perform the rectification using homographic transformation"""
        if len(self.corners) != 4:
            raise ValueError("Need exactly 4 corners for rectification")
            
        # Convert corners to original image coordinates
        corners_original = []
        for corner in self.corners:
            x_orig = int(corner[0] / self.scale_factor)
            y_orig = int(corner[1] / self.scale_factor)
            corners_original.append([x_orig, y_orig])
            
        # Source points (the selected corners)
        src_points = np.float32(corners_original)
        
        # Destination points (perfect rectangle)
        dst_points = np.float32([
            [0, 0],                                    # Top-left
            [self.output_size[0], 0],                  # Top-right
            [self.output_size[0], self.output_size[1]], # Bottom-right
            [0, self.output_size[1]]                   # Bottom-left
        ])
        
        # Calculate homography matrix
        homography_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # Apply transformation
        rectified = cv2.warpPerspective(
            self.original_image, 
            homography_matrix, 
            self.output_size
        )
        
        return rectified, homography_matrix
        
    def process_image(self, input_path, output_path=None):
        """Complete process: load, select corners, rectify, save"""
        print(f"Processing: {input_path}")
        
        # Load image
        if not self.load_image(input_path):
            return False
            
        # Interactive corner selection
        if not self.select_corners_interactive():
            return False
            
        # Rectify
        try:
            rectified_image, homography = self.rectify_facade()
            
            # Generate output path if not provided
            if output_path is None:
                input_path = Path(input_path)
                output_dir = input_path.parent.parent / "rectified"
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"{input_path.stem}_rectified.png"
            
            # Save rectified image
            cv2.imwrite(str(output_path), rectified_image)
            print(f"Rectified image saved to: {output_path}")
            
            # Save homography matrix for reference
            homography_path = str(output_path).replace('.png', '_homography.npy')
            np.save(homography_path, homography)
            
            # Show result
            cv2.imshow('Original', self.display_image)
            cv2.imshow('Rectified', rectified_image)
            print("Press any key to continue...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            return True
            
        except Exception as e:
            print(f"Error during rectification: {e}")
            return False

def convert_heic_to_jpg(input_dir, output_dir):
    """Convert HEIC/DNG files to JPG for easier processing"""
    try:
        from PIL import Image
        import pillow_heif
        
        # Register HEIF opener with Pillow
        pillow_heif.register_heif_opener()
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        converted_files = []
        
        for file_path in input_path.glob("*"):
            if file_path.suffix.lower() in ['.heic', '.dng']:
                try:
                    # Open and convert
                    image = Image.open(file_path)
                    output_file = output_path / f"{file_path.stem}.jpg"
                    image.save(output_file, "JPEG", quality=95)
                    converted_files.append(output_file)
                    print(f"Converted: {file_path.name} -> {output_file.name}")
                except Exception as e:
                    print(f"Failed to convert {file_path.name}: {e}")
                    
        return converted_files
        
    except ImportError:
        print("pillow_heif not installed. Install with: pip install pillow_heif")
        return []

if __name__ == "__main__":
    # Create rectifier
    rectifier = FacadeRectifier(output_size=(512, 512))
    
    # First, convert HEIC/DNG files to JPG
    raw_dir = "./pics-raw"
    converted_dir = "./pics-converted"
    
    print("Converting HEIC/DNG files to JPG...")
    converted_files = convert_heic_to_jpg(raw_dir, converted_dir)
    
    if not converted_files:
        print("No files converted. Using existing files in pics-converted or pics-raw...")
        # Look for existing JPG/PNG files
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            converted_files.extend(Path(converted_dir).glob(ext))
            
    if not converted_files:
        print("No suitable image files found!")
        exit(1)
    
    # Process each image
    for image_path in converted_files:
        print(f"\n--- Processing {image_path.name} ---")
        success = rectifier.process_image(image_path)
        
        if success:
            print(f"✓ Successfully processed {image_path.name}")
        else:
            print(f"✗ Failed to process {image_path.name}")
            
        # Ask if user wants to continue
        continue_processing = input("Continue with next image? (y/n): ").lower().strip()
        if continue_processing != 'y':
            break
            
    print("Processing complete!")
