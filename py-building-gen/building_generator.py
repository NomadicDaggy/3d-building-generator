"""
Soviet-Style Apartment Building Generator
Generates low-poly procedural buildings suitable for retro-style games
"""

import numpy as np
import trimesh
from typing import List, Tuple
import random


class BuildingGenerator:
    def __init__(self, seed=42):
        """Initialize the building generator with a seed for reproducibility"""
        random.seed(seed)
        np.random.seed(seed)
        
        # Building dimensions
        self.floor_height = 3.0
        self.apartment_width = 4.0
        self.building_depth = 8.0
        
        # Facade details
        self.window_width = 1.2
        self.window_height = 1.5
        self.window_depth = 0.2
        self.balcony_depth = 0.8
        self.balcony_height = 0.1
        
    def create_box(self, size, position=(0, 0, 0)):
        """Create a simple box mesh"""
        vertices = np.array([
            [0, 0, 0], [size[0], 0, 0], [size[0], size[1], 0], [0, size[1], 0],  # Front
            [0, 0, size[2]], [size[0], 0, size[2]], [size[0], size[1], size[2]], [0, size[1], size[2]]  # Back
        ]) + position
        
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # Front
            [4, 6, 5], [4, 7, 6],  # Back
            [0, 4, 5], [0, 5, 1],  # Bottom
            [2, 6, 7], [2, 7, 3],  # Top
            [0, 3, 7], [0, 7, 4],  # Left
            [1, 5, 6], [1, 6, 2]   # Right
        ])
        
        return trimesh.Trimesh(vertices=vertices, faces=faces)
    
    def create_window(self, position, with_frame=True):
        """Create a recessed window"""
        meshes = []
        
        # Window recess (negative space is simulated by inset geometry)
        recess = self.create_box(
            size=(self.window_width, self.window_height, self.window_depth),
            position=position
        )
        meshes.append(recess)
        
        if with_frame:
            # Window frame (thin border)
            frame_thickness = 0.05
            # Left frame
            left_frame = self.create_box(
                size=(frame_thickness, self.window_height, self.window_depth),
                position=position
            )
            # Right frame
            right_frame = self.create_box(
                size=(frame_thickness, self.window_height, self.window_depth),
                position=(position[0] + self.window_width - frame_thickness, position[1], position[2])
            )
            # Top frame
            top_frame = self.create_box(
                size=(self.window_width, frame_thickness, self.window_depth),
                position=(position[0], position[1] + self.window_height - frame_thickness, position[2])
            )
            # Bottom frame
            bottom_frame = self.create_box(
                size=(self.window_width, frame_thickness, self.window_depth),
                position=position
            )
            
            meshes.extend([left_frame, right_frame, top_frame, bottom_frame])
        
        return trimesh.util.concatenate(meshes)
    
    def create_balcony(self, position, width):
        """Create a simple balcony"""
        meshes = []
        
        # Balcony floor
        floor = self.create_box(
            size=(width, self.balcony_depth, self.balcony_height),
            position=position
        )
        meshes.append(floor)
        
        # Balcony railing (simple low-poly version)
        railing_height = 1.0
        railing_thickness = 0.05
        
        # Front railing
        front_rail = self.create_box(
            size=(width, railing_thickness, railing_height),
            position=(position[0], position[1] + self.balcony_depth - railing_thickness, position[2])
        )
        meshes.append(front_rail)
        
        # Side railings
        left_rail = self.create_box(
            size=(railing_thickness, self.balcony_depth, railing_height),
            position=position
        )
        right_rail = self.create_box(
            size=(railing_thickness, self.balcony_depth, railing_height),
            position=(position[0] + width - railing_thickness, position[1], position[2])
        )
        meshes.extend([left_rail, right_rail])
        
        return trimesh.util.concatenate(meshes)
    
    def create_apartment_facade(self, position, floor_num, variant=0):
        """
        Create a single apartment facade tile with variations
        variant: 0 = no balcony, 1 = balcony, 2 = double window
        """
        meshes = []
        x, y, z = position
        
        # Main wall section
        wall = self.create_box(
            size=(self.apartment_width, self.building_depth, self.floor_height),
            position=position
        )
        meshes.append(wall)
        
        # Window positioning (centered on facade)
        window_y_offset = 0.8  # From floor
        window_x_center = self.apartment_width / 2
        
        if variant == 2:  # Double window
            window_spacing = 0.3
            window_x1 = window_x_center - self.window_width - window_spacing / 2
            window_x2 = window_x_center + window_spacing / 2
            
            window1 = self.create_window((x + window_x1, y, z + window_y_offset))
            window2 = self.create_window((x + window_x2, y, z + window_y_offset))
            meshes.extend([window1, window2])
        else:  # Single window
            window_x = window_x_center - self.window_width / 2
            window = self.create_window((x + window_x, y, z + window_y_offset))
            meshes.append(window)
        
        # Add balcony if variant == 1
        if variant == 1:
            balcony_width = self.apartment_width * 0.8
            balcony_x = x + (self.apartment_width - balcony_width) / 2
            balcony_z = z + 0.2  # Slightly above floor
            
            balcony = self.create_balcony(
                (balcony_x, y - self.balcony_depth, balcony_z),
                balcony_width
            )
            meshes.append(balcony)
        
        return trimesh.util.concatenate(meshes)
    
    def create_base(self, width, depth):
        """Create ground floor base (often different in Soviet buildings)"""
        meshes = []
        
        # Base is slightly taller and might have different facade
        base_height = self.floor_height * 1.2
        
        # Main base structure
        base = self.create_box(
            size=(width, depth, base_height),
            position=(0, 0, 0)
        )
        meshes.append(base)
        
        # Entrance (simple recessed area)
        entrance_width = 2.0
        entrance_height = 2.5
        entrance_depth = 0.3
        entrance_x = width / 2 - entrance_width / 2
        
        entrance = self.create_box(
            size=(entrance_width, entrance_depth, entrance_height),
            position=(entrance_x, 0, 0.2)
        )
        meshes.append(entrance)
        
        # Some base windows (smaller, less regular)
        num_base_windows = int(width / self.apartment_width) - 1
        for i in range(num_base_windows):
            window_x = (i + 1) * self.apartment_width
            if abs(window_x - width / 2) > entrance_width:  # Don't place over entrance
                window = self.create_window(
                    (window_x, 0, base_height * 0.4),
                    with_frame=False
                )
                meshes.append(window)
        
        return trimesh.util.concatenate(meshes), base_height
    
    def create_roof(self, width, depth, height):
        """Create a simple flat roof with slight detail"""
        meshes = []
        
        roof_height = 0.3
        
        # Main roof slab
        roof = self.create_box(
            size=(width, depth, roof_height),
            position=(0, 0, height)
        )
        meshes.append(roof)
        
        # Roof edge detail (slight overhang)
        overhang = 0.2
        edge_height = 0.4
        
        # Front edge
        front_edge = self.create_box(
            size=(width + overhang * 2, overhang, edge_height),
            position=(-overhang, -overhang, height + roof_height)
        )
        meshes.append(front_edge)
        
        return trimesh.util.concatenate(meshes)
    
    def generate_building(self, num_floors=5, apartments_per_floor=4):
        """Generate complete building"""
        print(f"Generating {num_floors} story building with {apartments_per_floor} apartments per floor...")
        
        all_meshes = []
        
        building_width = apartments_per_floor * self.apartment_width
        
        # Create base
        print("Creating base...")
        base, base_height = self.create_base(building_width, self.building_depth)
        all_meshes.append(base)
        
        # Create middle floors
        current_height = base_height
        for floor in range(num_floors - 1):  # -1 because base is floor 0
            print(f"Creating floor {floor + 1}...")
            
            for apt in range(apartments_per_floor):
                # Vary the facade type
                variant = self.get_facade_variant(floor, apt)
                
                facade = self.create_apartment_facade(
                    position=(apt * self.apartment_width, 0, current_height),
                    floor_num=floor + 1,
                    variant=variant
                )
                all_meshes.append(facade)
            
            current_height += self.floor_height
        
        # Create roof
        print("Creating roof...")
        roof = self.create_roof(building_width, self.building_depth, current_height)
        all_meshes.append(roof)
        
        # Combine all meshes
        print("Combining meshes...")
        building = trimesh.util.concatenate(all_meshes)
        
        # Generate simple UV coordinates
        print("Generating UV coordinates...")
        building = self.generate_uvs(building)
        
        return building
    
    def get_facade_variant(self, floor, apartment):
        """Determine facade variant with some logic for variety"""
        # Create patterns: some floors have more balconies, etc.
        rand_val = (floor * 7 + apartment * 3) % 10
        
        if rand_val < 3:
            return 1  # Balcony
        elif rand_val < 6:
            return 0  # No balcony
        else:
            return 2  # Double window
    
    def generate_uvs(self, mesh):
        """Generate basic planar UV mapping"""
        # Simple box projection UV mapping
        vertices = mesh.vertices
        
        # Project onto XZ plane for horizontal surfaces
        # Project onto XY and ZY planes for vertical surfaces
        uvs = np.zeros((len(vertices), 2))
        
        # Simple planar projection (can be improved)
        uvs[:, 0] = vertices[:, 0] / 10.0  # Normalize X
        uvs[:, 1] = vertices[:, 2] / 10.0  # Normalize Z
        
        # Store UVs as visual (will be exported to OBJ)
        mesh.visual = trimesh.visual.TextureVisuals(uv=uvs)
        
        return mesh


def main():
    """Generate and export a Soviet-style apartment building"""
    
    generator = BuildingGenerator(seed=42)
    
    # Generate a 5-story building with 4 apartments per floor
    building = generator.generate_building(num_floors=5, apartments_per_floor=4)
    
    # Export to different formats
    print("\nExporting models...")
    
    # OBJ format (good for most game engines, preserves UVs)
    # building.export('soviet_apartment_block.obj')
    # print("✓ Exported to soviet_apartment_block.obj")
    
    # GLB format (modern format, good for web and modern engines)
    building.export('soviet_apartment_block.glb')
    print("✓ Exported to soviet_apartment_block.glb")
    
    # STL format (for 3D printing or backup)
    # building.export('soviet_apartment_block.stl')
    # print("✓ Exported to soviet_apartment_block.stl")
    
    print(f"\nBuilding statistics:")
    print(f"  Vertices: {len(building.vertices)}")
    print(f"  Faces: {len(building.faces)}")
    print(f"  Bounding box: {building.bounds}")
    print(f"  Volume: {building.volume:.2f} cubic units")
    
    print("\nDone! Models saved in current directory.")


if __name__ == "__main__":
    main()
