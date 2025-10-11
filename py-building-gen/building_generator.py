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
        
        # Window dimensions
        self.window_cavity_depth = 0.25  # Deep recess in wall
        self.window_reveal_depth = 0.15  # Distance from wall face to window frame
        self.window_frame_thickness = 0.05  # Thickness of window frame pieces
        self.window_glass_thickness = 0.02   # Thickness of glass pane
        
        # Define materials for different building components
        self.materials = {
            'wall': trimesh.visual.material.SimpleMaterial(
                diffuse=[220, 220, 220, 255],    # Light concrete gray
                ambient=[200, 200, 200, 255],
                specular=[50, 50, 50, 255]
            ),
            'base': trimesh.visual.material.SimpleMaterial(
                diffuse=[180, 160, 140, 255],    # Tan/beige for base
                ambient=[160, 140, 120, 255],
                specular=[40, 40, 40, 255]
            ),
            'window_cavity': trimesh.visual.material.SimpleMaterial(
                diffuse=[40, 40, 45, 255],       # Dark interior/shadow
                ambient=[30, 30, 35, 255],
                specular=[10, 10, 10, 255]
            ),
            'window': trimesh.visual.material.SimpleMaterial(
                diffuse=[100, 150, 200, 255],    # Blue-tinted glass
                ambient=[80, 120, 160, 255],
                specular=[150, 180, 220, 255]    # Reflective
            ),
            'window_frame': trimesh.visual.material.SimpleMaterial(
                diffuse=[60, 60, 60, 255],       # Dark gray metal
                ambient=[40, 40, 40, 255],
                specular=[80, 80, 80, 255]
            ),
            'balcony': trimesh.visual.material.SimpleMaterial(
                diffuse=[200, 180, 160, 255],    # Lighter tan/cream
                ambient=[180, 160, 140, 255],
                specular=[50, 50, 50, 255]
            ),
            'railing': trimesh.visual.material.SimpleMaterial(
                diffuse=[80, 80, 80, 255],       # Dark metallic gray
                ambient=[60, 60, 60, 255],
                specular=[120, 120, 120, 255]    # Metallic shine
            ),
            'roof': trimesh.visual.material.SimpleMaterial(
                diffuse=[120, 110, 100, 255],    # Dark brownish-gray
                ambient=[100, 90, 80, 255],
                specular=[30, 30, 30, 255]
            ),
            'entrance': trimesh.visual.material.SimpleMaterial(
                diffuse=[100, 80, 60, 255],      # Dark brown
                ambient=[80, 60, 40, 255],
                specular=[40, 40, 40, 255]
            )
        }
        
    def create_box(self, size, position=(0, 0, 0), material=None, solid=False):
        """Create a simple box mesh with Z as up axis and optional material"""
        # size = (width_X, depth_Y, height_Z)
        # Creates a box extending:
        #   - size[0] in X direction (width, left-right)
        #   - size[1] in Y direction (depth, front-back)
        #   - size[2] in Z direction (height, up-down)
        vertices = np.array([
            # Bottom face (Z=0)
            [0, 0, 0], [size[0], 0, 0], [size[0], size[1], 0], [0, size[1], 0],
            # Top face (Z=size[2])
            [0, 0, size[2]], [size[0], 0, size[2]], [size[0], size[1], size[2]], [0, size[1], size[2]]
        ]) + position
        
        faces = np.array([
            # Bottom face (normal pointing down)
            [0, 1, 2], [0, 2, 3],
            # Top face (normal pointing up)
            [4, 6, 5], [4, 7, 6],
            # Front face Y=0 (normal pointing toward -Y)
            [0, 4, 5], [0, 5, 1],
            # Back face Y=depth (normal pointing toward +Y)
            [2, 6, 7], [2, 7, 3],
            # Left face X=0 (normal pointing toward -X)
            [0, 3, 7], [0, 7, 4],
            # Right face X=width (normal pointing toward +X)
            [1, 5, 6], [1, 6, 2]
        ])
        
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Make solid if requested (for boolean operations)
        if solid:
            mesh.fix_normals()
            if not mesh.is_watertight:
                mesh.fill_holes()
        
        # Apply material if provided
        if material is not None:
            mesh.visual = trimesh.visual.TextureVisuals(material=material)
        
        return mesh
    
    def create_window_cavity(self, position):
        """Create the deep recess in the wall for the window (4 side walls only)"""
        meshes = []
        x, y, z = position
        wall_thickness = 0.05  # Thickness of cavity side walls
        
        # Bottom wall of cavity
        bottom = self.create_box(
            size=(self.window_width, self.window_cavity_depth, wall_thickness),
            position=(x, y, z),
            material=self.materials['window_cavity']
        )
        meshes.append(bottom)
        
        # Top wall of cavity
        top = self.create_box(
            size=(self.window_width, self.window_cavity_depth, wall_thickness),
            position=(x, y, z + self.window_height - wall_thickness),
            material=self.materials['window_cavity']
        )
        meshes.append(top)
        
        # Left wall of cavity
        left = self.create_box(
            size=(wall_thickness, self.window_cavity_depth, self.window_height),
            position=(x, y, z),
            material=self.materials['window_cavity']
        )
        meshes.append(left)
        
        # Right wall of cavity
        right = self.create_box(
            size=(wall_thickness, self.window_cavity_depth, self.window_height),
            position=(x + self.window_width - wall_thickness, y, z),
            material=self.materials['window_cavity']
        )
        meshes.append(right)
        
        return meshes
    
    def create_window(self, position, with_frame=True):
        """Create window assembly with frame and glass at proper depths within cavity"""
        meshes = []
        
        # Frame sits at reveal depth from wall face (inside the cavity)
        frame_y = position[1] + self.window_reveal_depth
        
        # Calculate frame outer dimensions (full window opening)
        frame_outer_width = self.window_width
        frame_outer_height = self.window_height
        
        # Frame depth (how thick the frame is front-to-back)
        frame_depth = 0.08
        
        # Glass will sit in the middle of the frame depth
        glass_y = frame_y + (frame_depth - self.window_glass_thickness) / 2
        
        if with_frame:
            # Create frame as 4 bars around the perimeter
            # Left frame (vertical bar on left side)
            left_frame = self.create_box(
                size=(self.window_frame_thickness, frame_depth, frame_outer_height),
                position=(position[0], frame_y, position[2]),
                material=self.materials['window_frame']
            )
            # Right frame (vertical bar on right side)
            right_frame = self.create_box(
                size=(self.window_frame_thickness, frame_depth, frame_outer_height),
                position=(position[0] + frame_outer_width - self.window_frame_thickness, frame_y, position[2]),
                material=self.materials['window_frame']
            )
            # Top frame (horizontal bar at top)
            top_frame = self.create_box(
                size=(frame_outer_width, frame_depth, self.window_frame_thickness),
                position=(position[0], frame_y, position[2] + frame_outer_height - self.window_frame_thickness),
                material=self.materials['window_frame']
            )
            # Bottom frame (horizontal bar at bottom)
            bottom_frame = self.create_box(
                size=(frame_outer_width, frame_depth, self.window_frame_thickness),
                position=(position[0], frame_y, position[2]),
                material=self.materials['window_frame']
            )
            
            meshes.extend([left_frame, right_frame, top_frame, bottom_frame])
        
        # Glass pane fills the frame opening (slightly smaller to account for frame thickness)
        glass_width = frame_outer_width - (2 * self.window_frame_thickness)
        glass_height = frame_outer_height - (2 * self.window_frame_thickness)
        
        window_glass = self.create_box(
            size=(glass_width, self.window_glass_thickness, glass_height),
            position=(position[0] + self.window_frame_thickness, glass_y, position[2] + self.window_frame_thickness),
            material=self.materials['window']
        )
        meshes.append(window_glass)
        
        return meshes
    
    def create_balcony(self, position, width):
        """Create a simple balcony"""
        meshes = []
        
        # Balcony floor - size = (width_X, depth_Y, height_Z)
        floor = self.create_box(
            size=(width, self.balcony_depth, self.balcony_height),
            position=position,
            material=self.materials['balcony']
        )
        meshes.append(floor)
        
        # Balcony railing (simple low-poly version)
        railing_height = 1.0
        railing_thickness = 0.05
        
        # Outer railing (farthest from building, at the front of the balcony Y=position[1])
        outer_rail = self.create_box(
            size=(width, railing_thickness, railing_height),
            position=(position[0], position[1], position[2] + self.balcony_height),
            material=self.materials['railing']
        )
        meshes.append(outer_rail)
        
        # Side railings
        left_rail = self.create_box(
            size=(railing_thickness, self.balcony_depth, railing_height),
            position=(position[0], position[1], position[2] + self.balcony_height),
            material=self.materials['railing']
        )
        right_rail = self.create_box(
            size=(railing_thickness, self.balcony_depth, railing_height),
            position=(position[0] + width - railing_thickness, position[1], position[2] + self.balcony_height),
            material=self.materials['railing']
        )
        meshes.extend([left_rail, right_rail])
        
        return meshes
    
    def create_apartment_facade(self, position, floor_num, variant=0):
        """
        Create a single apartment facade tile with variations
        variant: 0 = no balcony, 1 = balcony, 2 = double window
        """
        meshes = []
        x, y, z = position
        
        # Main wall section - size = (width_X, depth_Y, height_Z)
        wall = self.create_box(
            size=(self.apartment_width, self.building_depth, self.floor_height),
            position=position,
            material=self.materials['wall'],
            solid=True
        )
        
        # Window positioning (centered on facade, front face is at Y=y)
        window_z_offset = 0.8  # Height from floor
        window_x_center = self.apartment_width / 2
        boolean_depth = 0.5  # Depth of window cutout
        
        if variant == 2:  # Double window
            window_spacing = 0.3
            window_x1 = window_x_center - self.window_width - window_spacing / 2
            window_x2 = window_x_center + window_spacing / 2
            
            # Create both cutouts
            cutout1 = self.create_box(
                size=(self.window_width, boolean_depth, self.window_height),
                position=(x + window_x1, y, z + window_z_offset),
                solid=True
            )
            cutout2 = self.create_box(
                size=(self.window_width, boolean_depth, self.window_height),
                position=(x + window_x2, y, z + window_z_offset),
                solid=True
            )
            
            # Combine cutouts with union, then subtract from wall
            combined_cutout = cutout1.union(cutout2)
            wall = wall.difference(combined_cutout)
            
            # Create cavities first (starting at wall front face)
            cavity1_parts = self.create_window_cavity((x + window_x1, y, z + window_z_offset))
            cavity2_parts = self.create_window_cavity((x + window_x2, y, z + window_z_offset))
            meshes.extend(cavity1_parts)
            meshes.extend(cavity2_parts)
            
            # Then add window assemblies (same base position)
            window1_parts = self.create_window((x + window_x1, y, z + window_z_offset))
            window2_parts = self.create_window((x + window_x2, y, z + window_z_offset))
            meshes.extend(window1_parts)
            meshes.extend(window2_parts)
        else:  # Single window
            window_x = window_x_center - self.window_width / 2
            
            # Boolean cut for window
            cutout = self.create_box(
                size=(self.window_width, boolean_depth, self.window_height),
                position=(x + window_x, y, z + window_z_offset),
                solid=True
            )
            wall = wall.difference(cutout)
            
            # Create cavity first (starting at wall front face)
            cavity_parts = self.create_window_cavity((x + window_x, y, z + window_z_offset))
            meshes.extend(cavity_parts)
            
            # Then add window assembly (same base position)
            window_parts = self.create_window((x + window_x, y, z + window_z_offset))
            meshes.extend(window_parts)
        
        # Re-apply material after boolean operations
        wall.visual = trimesh.visual.TextureVisuals(material=self.materials['wall'])
        meshes.append(wall)
        
        # Add balcony if variant == 1
        # Balcony extends in NEGATIVE Y direction from building front
        if variant == 1:
            balcony_width = self.apartment_width * 0.8
            balcony_x = x + (self.apartment_width - balcony_width) / 2
            balcony_z = z + 0.2  # Slightly above floor
            
            balcony_parts = self.create_balcony(
                (balcony_x, y - self.balcony_depth, balcony_z),
                balcony_width
            )
            meshes.extend(balcony_parts)
        
        return meshes
    
    def create_base(self, width, depth):
        """Create ground floor base (often different in Soviet buildings)"""
        meshes = []
        
        # Base is slightly taller and might have different facade
        base_height = self.floor_height * 1.2
        boolean_depth = 0.5  # Depth of cutouts
        
        # Main base structure - size = (width_X, depth_Y, height_Z)
        base = self.create_box(
            size=(width, depth, base_height),
            position=(0, 0, 0),
            material=self.materials['base'],
            solid=True
        )
        
        # Entrance cutout and overlay
        entrance_width = 2.0
        entrance_height = 2.5
        entrance_depth = 0.01  # Very thin overlay, just for color
        entrance_x = width / 2 - entrance_width / 2
        
        # Boolean cut for entrance
        entrance_cutout = self.create_box(
            size=(entrance_width, boolean_depth, entrance_height),
            position=(entrance_x, 0, 0.2),
            solid=True
        )
        base = base.difference(entrance_cutout)
        
        # Entrance overlay (colored rectangle at the back of the recess)
        entrance = self.create_box(
            size=(entrance_width, entrance_depth, entrance_height),
            position=(entrance_x, boolean_depth - entrance_depth, 0.2),
            material=self.materials['entrance']
        )
        meshes.append(entrance)
        
        # Some base windows (smaller, less regular)
        num_base_windows = int(width / self.apartment_width) - 1
        window_cutouts = []
        window_positions = []
        
        # Collect all window positions and create cutouts
        for i in range(num_base_windows):
            window_x = (i + 1) * self.apartment_width
            if abs(window_x - width / 2) > entrance_width:  # Don't place over entrance
                window_positions.append(window_x)
                # Create cutout
                cutout = self.create_box(
                    size=(self.window_width, boolean_depth, self.window_height),
                    position=(window_x, 0, base_height * 0.4),
                    solid=True
                )
                window_cutouts.append(cutout)
        
        # Combine all window cutouts and subtract from base in one operation
        if window_cutouts:
            if len(window_cutouts) == 1:
                combined_cutouts = window_cutouts[0]
            else:
                combined_cutouts = window_cutouts[0]
                for cutout in window_cutouts[1:]:
                    combined_cutouts = combined_cutouts.union(cutout)
            base = base.difference(combined_cutouts)
        
        # Now add window details (cavities and windows)
        for window_x in window_positions:
            # Create cavity (starting at wall front face)
            cavity_parts = self.create_window_cavity((window_x, 0, base_height * 0.4))
            meshes.extend(cavity_parts)
            
            # Add window
            window_parts = self.create_window(
                (window_x, 0, base_height * 0.4),
                with_frame=False
            )
            meshes.extend(window_parts)
        
        # Re-apply material after boolean operations
        base.visual = trimesh.visual.TextureVisuals(material=self.materials['base'])
        meshes.append(base)
        return meshes, base_height
    
    def create_roof(self, width, depth, height):
        """Create a simple flat roof with slight detail"""
        meshes = []
        
        roof_height = 0.3
        
        # Main roof slab - size = (width_X, depth_Y, height_Z)
        roof = self.create_box(
            size=(width, depth, roof_height),
            position=(0, 0, height),
            material=self.materials['roof']
        )
        meshes.append(roof)
        
        # Roof edge detail (slight overhang)
        overhang = 0.2
        edge_height = 0.4
        
        # Front edge
        front_edge = self.create_box(
            size=(width + overhang * 2, overhang, edge_height),
            position=(-overhang, -overhang, height + roof_height),
            material=self.materials['roof']
        )
        meshes.append(front_edge)
        
        return meshes
    
    def generate_building(self, num_floors=5, apartments_per_floor=4):
        """Generate complete building"""
        print(f"Generating {num_floors} story building with {apartments_per_floor} apartments per floor...")
        
        # Use Scene to preserve materials
        scene = trimesh.Scene()
        mesh_counter = 0
        
        building_width = apartments_per_floor * self.apartment_width
        
        # Create base
        print("Creating base...")
        base_parts, base_height = self.create_base(building_width, self.building_depth)
        for part in base_parts:
            scene.add_geometry(part, node_name=f'base_{mesh_counter}')
            mesh_counter += 1
        
        # Create middle floors
        current_height = base_height
        for floor in range(num_floors - 1):  # -1 because base is floor 0
            print(f"Creating floor {floor + 1}...")
            
            for apt in range(apartments_per_floor):
                # Vary the facade type
                variant = self.get_facade_variant(floor, apt)
                
                facade_parts = self.create_apartment_facade(
                    position=(apt * self.apartment_width, 0, current_height),
                    floor_num=floor + 1,
                    variant=variant
                )
                for part in facade_parts:
                    scene.add_geometry(part, node_name=f'facade_f{floor}_a{apt}_{mesh_counter}')
                    mesh_counter += 1
            
            current_height += self.floor_height
        
        # Create roof
        print("Creating roof...")
        roof_parts = self.create_roof(building_width, self.building_depth, current_height)
        for part in roof_parts:
            scene.add_geometry(part, node_name=f'roof_{mesh_counter}')
            mesh_counter += 1
        
        print(f"Created {mesh_counter} individual meshes with materials!")
        
        # Rotation for blender
        rotation_matrix = trimesh.transformations.rotation_matrix(
            angle=np.radians(-90),  # 90 degrees
            direction=[1, 0, 0],   # Rotate around X-axis
            point=[0, 0, 0]        # Rotate around the origin (front-bottom edge)
        )
        scene.apply_transform(rotation_matrix)
        
        return scene
    
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


def main():
    """Generate and export a Soviet-style apartment building"""
    
    generator = BuildingGenerator(seed=42)
    
    # Generate a 5-story building with 4 apartments per floor
    building_scene = generator.generate_building(num_floors=5, apartments_per_floor=4)
    
    # OBJ+MTL format (preserves materials for Blender)
    building_scene.export('soviet_apartment_block.obj')
    
    print(f"\nBuilding statistics:")
    print(f"  Meshes in scene: {len(building_scene.geometry)}")
    total_vertices = sum(len(mesh.vertices) for mesh in building_scene.geometry.values())
    total_faces = sum(len(mesh.faces) for mesh in building_scene.geometry.values())
    print(f"  Total vertices: {total_vertices}")
    print(f"  Total faces: {total_faces}")
    print(f"  Bounding box: {building_scene.bounds}")


if __name__ == "__main__":
    main()
