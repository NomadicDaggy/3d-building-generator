"""
Facade Rectification Pipeline - Fullscreen Interface
Works directly with HEIC/DNG/JPEG files with fullscreen display for maximum detail
"""

import cv2
import numpy as np
import os
from pathlib import Path

class FacadeRectifier:
    def __init__(self, preserve_aspect_ratio=True, max_output_width=None, fullscreen=True):
        """
        Initialize rectifier
        
        Args:
            preserve_aspect_ratio: If True, maintains the aspect ratio of selected area
            max_output_width: Optional max width to prevent huge outputs (None = no limit)
            fullscreen: If True, uses fullscreen display for maximum detail
        """
        self.preserve_aspect_ratio = preserve_aspect_ratio
        self.max_output_width = max_output_width
        self.fullscreen = fullscreen
        self.corners = []
        self.current_image = None
        self.original_image = None
        self.corner_selection_started = False
        self.screen_width = None
        self.screen_height = None
        
    def get_screen_resolution(self):
        """Get screen resolution for fullscreen display"""
        try:
            import tkinter as tk
            root = tk.Tk()
            self.screen_width = root.winfo_screenwidth()
            self.screen_height = root.winfo_screenheight()
            root.destroy()
            
            # Leave some padding for taskbars/menus (100px each side)
            self.screen_width -= 200
            self.screen_height -= 200
            
            print(f"Screen resolution detected: {self.screen_width}x{self.screen_height} (with padding)")
            
        except Exception as e:
            print(f"Could not detect screen resolution: {e}")
            # Fallback to common large resolution
            self.screen_width = 1720
            self.screen_height = 880
            print(f"Using fallback resolution: {self.screen_width}x{self.screen_height}")
        
    def mouse_callback(self, event, x, y, flags, param):
        """Mouse callback for selecting facade corners"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.corners) < 4:
                # Mark that corner selection has started
                self.corner_selection_started = True
                
                self.corners.append((x, y))
                # Draw point on image with larger markers for visibility
                cv2.circle(self.current_image, (x, y), 8, (0, 255, 0), -1)
                cv2.circle(self.current_image, (x, y), 12, (255, 255, 255), 2)
                cv2.putText(self.current_image, str(len(self.corners)), 
                           (x+15, y-15), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                print(f"Corner {len(self.corners)}: ({x}, {y})")
                
                if len(self.corners) == 4:
                    print("All 4 corners selected! Press 'r' to rectify or 'c' to clear")
    
    def load_image_file(self, image_path):
        """Load image from various formats (HEIC, DNG, JPEG, PNG) directly"""
        file_path = Path(image_path)
        file_ext = file_path.suffix.lower()
        
        try:
            if file_ext in ['.heic', '.dng']:
                # Use Pillow for HEIC/DNG files
                try:
                    from PIL import Image
                    import pillow_heif
                    
                    # Register HEIF opener with Pillow
                    pillow_heif.register_heif_opener()
                    
                    # Open with Pillow
                    pil_image = Image.open(image_path)
                    
                    # Convert to RGB if necessary
                    if pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    
                    # Convert to numpy array (PIL uses RGB, OpenCV uses BGR)
                    image_array = np.array(pil_image)
                    # Convert RGB to BGR for OpenCV
                    image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    
                    print(f"Loaded {file_ext.upper()} file directly: {file_path.name}")
                    return image_bgr
                    
                except ImportError:
                    print("pillow_heif not installed. Install with: pip install pillow_heif")
                    return None
                    
            else:
                # Use OpenCV for standard formats (JPEG, PNG, etc.)
                image = cv2.imread(str(image_path))
                if image is not None:
                    print(f"Loaded {file_ext.upper()} file: {file_path.name}")
                return image
                
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
            return None
                    
    def load_image(self, image_path):
        """Load and prepare image for rectification"""
        self.original_image = self.load_image_file(image_path)
        if self.original_image is None:
            raise ValueError(f"Could not load image: {image_path}")
            
        # Reset corner selection state
        self.corners = []
        self.corner_selection_started = False
        
        # Get screen resolution if not already done
        if self.screen_width is None or self.screen_height is None:
            self.get_screen_resolution()
            
        # Scale image to FIT WITHIN screen bounds while preserving aspect ratio
        height, width = self.original_image.shape[:2]
        
        if self.fullscreen:
            # Calculate scale to fit ENTIRE image within screen bounds
            scale_w = self.screen_width / width
            scale_h = self.screen_height / height
            # Use the smaller scale to ensure entire image fits
            scale = min(scale_w, scale_h)
            
            # Don't upscale small images
            if scale > 1.0:
                scale = 1.0
                
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            self.display_image = cv2.resize(self.original_image, (new_width, new_height))
            self.scale_factor = scale
        else:
            # Legacy smaller window mode
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
        print(f"Original image size: {width}x{height}")
        print(f"Display size: {self.display_image.shape[1]}x{self.display_image.shape[0]}")
        print(f"Scale factor: {self.scale_factor:.3f}")
        return True
        
    def setup_window(self):
        """Setup the display window"""
        window_name = 'Facade Rectifier'
        
        if self.fullscreen:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            print("Fullscreen mode enabled (Press ESC to exit fullscreen)")
        else:
            cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
            
        return window_name
        
    def update_window_title(self, current_index, total_images, image_name, window_name):
        """Update window title with current image info"""
        title = f"Facade Rectifier - {current_index + 1}/{total_images} - {image_name}"
        cv2.setWindowTitle(window_name, title)
        
    def draw_instructions(self, image):
        """Draw instructions on the image"""
        # Create a copy to draw on
        img_with_text = image.copy()
        
        # Instructions text - larger font for fullscreen
        font_scale = 0.8 if self.fullscreen else 0.5
        thickness = 2 if self.fullscreen else 1
        
        instructions = [
            "Controls:",
            "  Click: Select corners (1-4)",
            "  A: Previous image",
            "  D: Next image", 
            "  C: Clear corners",
            "  R: Rectify (4 corners)",
            "  Q: Quit",
            "  ESC: Toggle fullscreen"
        ]
        
        # Calculate text size for background
        text_height = int(25 * font_scale)
        bg_height = len(instructions) * text_height + 40
        bg_width = 350 if self.fullscreen else 280
        
        # Draw semi-transparent background
        overlay = img_with_text.copy()
        cv2.rectangle(overlay, (15, 15), (bg_width, bg_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, img_with_text, 0.2, 0, img_with_text)
        
        # Draw text
        y_offset = 40
        for line in instructions:
            cv2.putText(img_with_text, line, (25, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
            y_offset += text_height
            
        # Show navigation status
        status_color = (0, 0, 255) if self.corner_selection_started else (0, 255, 0)
        status_text = "Navigation locked" if self.corner_selection_started else "Navigation enabled"
        cv2.putText(img_with_text, status_text, (25, y_offset + 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, status_color, thickness)
            
        return img_with_text
        
    def select_corners_interactive(self, image_list, current_index=0):
        """Interactive corner selection with navigation"""
        total_images = len(image_list)
        current_idx = current_index
        
        print("=== Facade Rectifier - Fullscreen Interface ===")
        print("Navigate through images:")
        print("  A - Previous image")
        print("  D - Next image")
        print("Select corners (click in order):")
        print("1. Top-left, 2. Top-right, 3. Bottom-right, 4. Bottom-left")
        print("Other controls:")
        print("  C - Clear corners")
        print("  R - Rectify (when 4 corners selected)")
        print("  Q - Quit")
        print("  ESC - Toggle fullscreen")
        
        window_name = self.setup_window()
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        # Load initial image
        if not self.load_image(image_list[current_idx]):
            return None, None
            
        while True:
            # Update window title
            self.update_window_title(current_idx, total_images, image_list[current_idx].name, window_name)
            
            # Draw instructions on image
            display_img = self.draw_instructions(self.current_image)
            
            cv2.imshow(window_name, display_img)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                cv2.destroyAllWindows()
                return None, None
                
            elif key == 27:  # ESC key - toggle fullscreen
                self.fullscreen = not self.fullscreen
                cv2.destroyWindow(window_name)
                window_name = self.setup_window()
                cv2.setMouseCallback(window_name, self.mouse_callback)
                # Reload current image with new display settings
                self.load_image(image_list[current_idx])
                print(f"Fullscreen {'enabled' if self.fullscreen else 'disabled'}")
                
            elif key == ord('a'):  # Previous image
                if not self.corner_selection_started and current_idx > 0:
                    current_idx -= 1
                    print(f"\n← Previous image: {image_list[current_idx].name}")
                    if not self.load_image(image_list[current_idx]):
                        continue
                    self.current_image = self.display_image.copy()
                elif self.corner_selection_started:
                    print("Cannot navigate - corner selection in progress. Press 'c' to clear first.")
                else:
                    print("Already at first image.")
                    
            elif key == ord('d'):  # Next image
                if not self.corner_selection_started and current_idx < total_images - 1:
                    current_idx += 1
                    print(f"\n→ Next image: {image_list[current_idx].name}")
                    if not self.load_image(image_list[current_idx]):
                        continue
                    self.current_image = self.display_image.copy()
                elif self.corner_selection_started:
                    print("Cannot navigate - corner selection in progress. Press 'c' to clear first.")
                else:
                    print("Already at last image.")
                    
            elif key == ord('c'):
                # Clear corners and reset image
                self.corners = []
                self.corner_selection_started = False
                self.current_image = self.display_image.copy()
                print("Corners cleared - navigation enabled")
                    
            elif key == ord('r') and len(self.corners) == 4:
                cv2.destroyAllWindows()
                return image_list[current_idx], current_idx
                
    def calculate_output_dimensions(self, corners_original):
        """Calculate optimal output dimensions based on selected area"""
        corners = np.array(corners_original)
        
        # Calculate width and height of the selected rectangle
        # Use the longer edges to determine dimensions
        top_width = np.linalg.norm(corners[1] - corners[0])
        bottom_width = np.linalg.norm(corners[2] - corners[3])
        left_height = np.linalg.norm(corners[3] - corners[0])
        right_height = np.linalg.norm(corners[2] - corners[1])
        
        # Use average of parallel edges
        width = int((top_width + bottom_width) / 2)
        height = int((left_height + right_height) / 2)
        
        # Apply max width constraint if specified
        if self.max_output_width and width > self.max_output_width:
            scale_factor = self.max_output_width / width
            width = self.max_output_width
            height = int(height * scale_factor)
            
        print(f"Calculated output dimensions: {width}x{height}")
        return width, height
        
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
            
        # Calculate output dimensions
        output_width, output_height = self.calculate_output_dimensions(corners_original)
        
        # Source points (the selected corners)
        src_points = np.float32(corners_original)
        
        # Destination points (perfect rectangle at calculated dimensions)
        dst_points = np.float32([
            [0, 0],                           # Top-left
            [output_width, 0],                # Top-right
            [output_width, output_height],    # Bottom-right
            [0, output_height]                # Bottom-left
        ])
        
        # Calculate homography matrix
        homography_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # Apply transformation
        rectified = cv2.warpPerspective(
            self.original_image, 
            homography_matrix, 
            (output_width, output_height)
        )
        
        return rectified, homography_matrix, (output_width, output_height)
        
    def process_image(self, input_path, output_path=None):
        """Complete process: load, select corners, rectify, save"""
        print(f"\nProcessing: {input_path}")
        
        # Rectify
        try:
            rectified_image, homography, dimensions = self.rectify_facade()
            
            # Generate output path if not provided
            if output_path is None:
                input_path = Path(input_path)
                output_dir = input_path.parent.parent / "rectified"
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"{input_path.stem}_rectified.png"
            
            # Save rectified image (PNG for lossless quality)
            cv2.imwrite(str(output_path), rectified_image)
            print(f"Rectified image saved to: {output_path}")
            print(f"Output dimensions: {dimensions[0]}x{dimensions[1]}")
            
            # Save homography matrix for reference
            homography_path = str(output_path).replace('.png', '_homography.npy')
            np.save(homography_path, homography)
            
            # Save metadata
            metadata_path = str(output_path).replace('.png', '_metadata.txt')
            with open(metadata_path, 'w') as f:
                f.write(f"Source: {input_path}\n")
                f.write(f"Output dimensions: {dimensions[0]}x{dimensions[1]}\n")
                f.write(f"Original corners (in source coordinates):\n")
                for i, corner in enumerate(self.corners):
                    orig_x = int(corner[0] / self.scale_factor)
                    orig_y = int(corner[1] / self.scale_factor)
                    f.write(f"  Corner {i+1}: ({orig_x}, {orig_y})\n")
                f.write(f"Scale factor used for display: {self.scale_factor:.3f}\n")
            
            # Show result in fullscreen
            cv2.namedWindow('Original vs Rectified', cv2.WINDOW_NORMAL)
            if self.fullscreen:
                cv2.setWindowProperty('Original vs Rectified', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            # Create side-by-side comparison
            display_original = self.display_image
            
            # Scale rectified for display
            if rectified_image.shape[1] > self.screen_width//2 or rectified_image.shape[0] > self.screen_height:
                scale = min((self.screen_width//2)/rectified_image.shape[1], self.screen_height/rectified_image.shape[0])
                new_width = int(rectified_image.shape[1] * scale)
                new_height = int(rectified_image.shape[0] * scale)
                display_rectified = cv2.resize(rectified_image, (new_width, new_height))
            else:
                display_rectified = rectified_image
            
            # Create side-by-side image
            max_height = max(display_original.shape[0], display_rectified.shape[0])
            
            # Resize both to same height for comparison
            if display_original.shape[0] != max_height:
                scale = max_height / display_original.shape[0]
                new_width = int(display_original.shape[1] * scale)
                display_original = cv2.resize(display_original, (new_width, max_height))
                
            if display_rectified.shape[0] != max_height:
                scale = max_height / display_rectified.shape[0]
                new_width = int(display_rectified.shape[1] * scale)
                display_rectified = cv2.resize(display_rectified, (new_width, max_height))
            
            # Combine images
            comparison = np.hstack([display_original, display_rectified])
            
            cv2.imshow('Original vs Rectified', comparison)
            print("Press any key to continue...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            return True
            
        except Exception as e:
            print(f"Error during rectification: {e}")
            return False

def find_source_images(raw_dir):
    """Find all supported image files in the raw directory"""
    raw_path = Path(raw_dir)
    
    if not raw_path.exists():
        print(f"Directory not found: {raw_dir}")
        return []
    
    # Supported formats
    supported_extensions = ['.heic', '.dng', '.jpg', '.jpeg', '.png']
    
    image_files = []
    for ext in supported_extensions:
        image_files.extend(raw_path.glob(f"*{ext}"))
        image_files.extend(raw_path.glob(f"*{ext.upper()}"))
    
    if image_files:
        print(f"Found {len(image_files)} image files:")
        for f in sorted(image_files):
            print(f"  {f.name}")
    else:
        print(f"No supported image files found in {raw_dir}")
        print(f"Supported formats: {', '.join(supported_extensions)}")
    
    return sorted(image_files)

if __name__ == "__main__":
    # Configuration
    PRESERVE_ASPECT_RATIO = True
    MAX_OUTPUT_WIDTH = 4096  # Set to None for no limit, or e.g. 4096 to cap at 4K width
    FULLSCREEN = True        # Start in fullscreen mode
    
    # Create rectifier
    rectifier = FacadeRectifier(
        preserve_aspect_ratio=PRESERVE_ASPECT_RATIO,
        max_output_width=MAX_OUTPUT_WIDTH,
        fullscreen=FULLSCREEN
    )
    
    # Find source images directly - CORRECT DIRECTORY PATH
    raw_dir = "./pics-raw"  # Same directory level as script
    source_files = find_source_images(raw_dir)
    
    if not source_files:
        print("No suitable image files found!")
        exit(1)
    
    print(f"\nConfiguration:")
    print(f"  Working directly with source files")
    print(f"  Fullscreen mode: {FULLSCREEN}")
    print(f"  Preserve aspect ratio: {PRESERVE_ASPECT_RATIO}")
    print(f"  Max output width: {MAX_OUTPUT_WIDTH if MAX_OUTPUT_WIDTH else 'No limit'}")
    print(f"  Output format: PNG (lossless)")
    print(f"  Total images found: {len(source_files)}")
    
    print(f"\nStarting fullscreen interface...")
    print(f"Use A/D to navigate, click corners to select, R to rectify, ESC to toggle fullscreen")
    
    # Main navigation loop
    current_index = 0
    
    while current_index < len(source_files):
        # Interactive selection with navigation
        selected_image, selected_index = rectifier.select_corners_interactive(
            source_files, current_index
        )
        
        if selected_image is None:
            print("Exiting...")
            break
            
        # Process the selected image
        print(f"\n{'='*50}")
        print(f"Rectifying {selected_image.name}")
        print(f"{'='*50}")
        
        success = rectifier.process_image(selected_image)
        
        if success:
            print(f"✓ Successfully processed {selected_image.name}")
        else:
            print(f"✗ Failed to process {selected_image.name}")
            
        # Move to next image for next iteration
        current_index = selected_index + 1
        
        # Ask if user wants to continue or go back to navigation
        if current_index < len(source_files):
            choice = input("\nWhat next? (n)ext image, (r)estart navigation, (q)uit: ").lower().strip()
            if choice == 'q':
                break
            elif choice == 'r':
                current_index = 0
            # else continue to next image (default)
            
    print("\nProcessing complete!")
    print("Check the 'rectified/' folder for your high-resolution rectified facades.")
