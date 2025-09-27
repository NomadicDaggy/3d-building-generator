"""
Facade Rectification Pipeline - Maximized Window Style
Image size independent of window, maximized instead of fullscreen
"""

import cv2
import numpy as np
import os
from pathlib import Path

class FacadeRectifier:
    def __init__(self, preserve_aspect_ratio=True, max_output_width=None, maximized=True):
        """
        Initialize rectifier
        
        Args:
            preserve_aspect_ratio: If True, maintains the aspect ratio of selected area
            max_output_width: Optional max width to prevent huge outputs (None = no limit)
            maximized: If True, uses maximized window for maximum detail
        """
        self.preserve_aspect_ratio = preserve_aspect_ratio
        self.max_output_width = max_output_width
        self.maximized = maximized
        self.corners = []
        self.current_image = None
        self.original_image = None
        self.corner_selection_started = False
        self.display_image = None
        self.scale_factor = 1.0
        
    def get_window_size(self):
        """Get reasonable window dimensions"""
        try:
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            if self.maximized:
                # Use most of screen but leave space for title bar and taskbar
                return screen_width - 100, screen_height - 150
            else:
                # Standard large window
                return 1200, 800
        except:
            return 1200, 800  # Fallback
        
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
    
    def create_display_image(self, image):
        """Create a properly sized display image"""
        height, width = image.shape[:2]
        
        # Get target window size
        window_w, window_h = self.get_window_size()
        
        # Calculate scale to fit image within window
        scale_w = window_w / width
        scale_h = window_h / height
        scale = min(scale_w, scale_h, 1.0)  # Don't upscale
        
        # Calculate new dimensions
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize image
        scaled_image = cv2.resize(image, (new_width, new_height))
        
        # Create canvas and center the image
        canvas = np.zeros((window_h, window_w, 3), dtype=np.uint8)
        
        # Calculate position to center image
        start_y = (window_h - new_height) // 2
        start_x = (window_w - new_width) // 2
        
        # Place image on canvas
        canvas[start_y:start_y + new_height, start_x:start_x + new_width] = scaled_image
        
        # Update corner coordinates offset
        self.image_offset_x = start_x
        self.image_offset_y = start_y
        self.scale_factor = scale
        
        return canvas
                    
    def load_image(self, image_path):
        """Load and prepare image for rectification"""
        self.original_image = self.load_image_file(image_path)
        if self.original_image is None:
            raise ValueError(f"Could not load image: {image_path}")
            
        # Reset corner selection state
        self.corners = []
        self.corner_selection_started = False
        
        # Create properly sized display image
        self.display_image = self.create_display_image(self.original_image)
        self.current_image = self.display_image.copy()
        
        height, width = self.original_image.shape[:2]
        print(f"Original image size: {width}x{height}")
        print(f"Display size: {self.display_image.shape[1]}x{self.display_image.shape[0]}")
        print(f"Scale factor: {self.scale_factor:.3f}")
        
        return True
        
    def setup_window(self):
        """Setup the display window"""
        window_name = 'Facade Rectifier'
        
        # Create normal resizable window
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        if self.maximized:
            # Get window size and set it
            window_w, window_h = self.get_window_size()
            cv2.resizeWindow(window_name, window_w, window_h)
            print(f"Maximized window mode: {window_w}x{window_h}")
        else:
            # Standard window size
            cv2.resizeWindow(window_name, 1200, 800)
            print("Standard window mode: 1200x800")
            
        return window_name
        
    def update_window_title(self, current_index, total_images, image_name, window_name):
        """Update window title with current image info"""
        title = f"Facade Rectifier - {current_index + 1}/{total_images} - {image_name}"
        cv2.setWindowTitle(window_name, title)
        
    def draw_instructions(self, image):
        """Draw instructions on the image"""
        # Create a copy to draw on
        img_with_text = image.copy()
        
        # Instructions text - scale based on image size
        height, width = image.shape[:2]
        font_scale = max(0.5, min(1.0, width / 2000))
        thickness = max(1, int(font_scale * 2))
        
        instructions = [
            "Controls:",
            "  Click: Select corners (1-4)",
            "  A: Previous image",
            "  D: Next image", 
            "  C: Clear corners",
            "  R: Rectify (4 corners)",
            "  Q: Quit",
            "  M: Toggle window size"
        ]
        
        # Calculate text size for background
        text_height = int(25 * font_scale)
        bg_height = len(instructions) * text_height + 40
        bg_width = int(300 * font_scale)
        
        # Draw semi-transparent background
        overlay = img_with_text.copy()
        cv2.rectangle(overlay, (15, 15), (bg_width, bg_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, img_with_text, 0.2, 0, img_with_text)
        
        # Draw text
        y_offset = int(35 * font_scale)
        for line in instructions:
            cv2.putText(img_with_text, line, (25, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
            y_offset += text_height
            
        # Show navigation status
        status_color = (0, 0, 255) if self.corner_selection_started else (0, 255, 0)
        status_text = "Navigation locked" if self.corner_selection_started else "Navigation enabled"
        cv2.putText(img_with_text, status_text, (25, y_offset + 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, status_color, thickness)
            
        return img_with_text
        
    def adjust_corner_coordinates(self, x, y):
        """Adjust corner coordinates for image offset and scaling"""
        # Adjust for image position on canvas
        adjusted_x = x - self.image_offset_x
        adjusted_y = y - self.image_offset_y
        
        # Convert to original image coordinates
        orig_x = adjusted_x / self.scale_factor
        orig_y = adjusted_y / self.scale_factor
        
        return int(orig_x), int(orig_y)
        
    def select_corners_interactive(self, image_list, current_index=0):
        """Interactive corner selection with navigation"""
        total_images = len(image_list)
        current_idx = current_index
        
        print("=== Facade Rectifier - Maximized Window ===")
        print("Navigate through images:")
        print("  A - Previous image")
        print("  D - Next image")
        print("Select corners (click in order):")
        print("1. Top-left, 2. Top-right, 3. Bottom-right, 4. Bottom-left")
        print("Other controls:")
        print("  C - Clear corners")
        print("  R - Rectify (when 4 corners selected)")
        print("  Q - Quit")
        print("  M - Toggle window size")
        
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
            
            # Check if window was closed (returns -1 when window is closed)
            key = cv2.waitKey(30) & 0xFF
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                cv2.destroyAllWindows()
                return None, None
            
            if key == ord('q'):
                cv2.destroyAllWindows()
                return None, None
                
            elif key == ord('m'):  # Toggle window size
                self.maximized = not self.maximized
                cv2.destroyWindow(window_name)
                # Reload image with new display mode
                self.load_image(image_list[current_idx])
                window_name = self.setup_window()
                cv2.setMouseCallback(window_name, self.mouse_callback)
                print(f"Window size: {'Maximized' if self.maximized else 'Standard'}")
                
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
            orig_x, orig_y = self.adjust_corner_coordinates(corner[0], corner[1])
            corners_original.append([orig_x, orig_y])
            
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
                    orig_x, orig_y = self.adjust_corner_coordinates(corner[0], corner[1])
                    f.write(f"  Corner {i+1}: ({orig_x}, {orig_y})\n")
                f.write(f"Scale factor used for display: {self.scale_factor:.3f}\n")
                f.write(f"Image offset: ({self.image_offset_x}, {self.image_offset_y})\n")
            
            # Show result
            result_display = self.create_display_image(rectified_image)
            cv2.namedWindow('Rectified Result', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Rectified Result', result_display.shape[1], result_display.shape[0])
            cv2.imshow('Rectified Result', result_display)
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
    MAXIMIZED = True         # Start with maximized window
    
    # Create rectifier
    rectifier = FacadeRectifier(
        preserve_aspect_ratio=PRESERVE_ASPECT_RATIO,
        max_output_width=MAX_OUTPUT_WIDTH,
        maximized=MAXIMIZED
    )
    
    # Find source images directly
    raw_dir = "./pics-raw"
    source_files = find_source_images(raw_dir)
    
    if not source_files:
        print("No suitable image files found!")
        exit(1)
    
    print(f"\nConfiguration:")
    print(f"  Working directly with source files")
    print(f"  Maximized window mode (stays on current monitor)")
    print(f"  Window mode: {'Maximized' if MAXIMIZED else 'Standard'}")
    print(f"  Preserve aspect ratio: {PRESERVE_ASPECT_RATIO}")
    print(f"  Max output width: {MAX_OUTPUT_WIDTH if MAX_OUTPUT_WIDTH else 'No limit'}")
    print(f"  Output format: PNG (lossless)")
    print(f"  Total images found: {len(source_files)}")
    
    print(f"\nStarting interface...")
    print(f"Use A/D to navigate, click corners to select, R to rectify, M to toggle window size")
    print(f"You can close the window with the X button or press Q")
    
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
