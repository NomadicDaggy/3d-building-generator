# Texturing Guide

## UV Mapping Strategy

The buildings are UV mapped using simple planar projection. Here's how to texture them:

## Method 1: Procedural Texturing (Recommended)

Since the building is 100% procedural, you can texture it procedurally too:

### In Blender:
1. Import the OBJ file
2. Use Shader Editor with these nodes:
   - **Texture Coordinate** → Object
   - **Mapping** → adjust scale per axis
   - **Noise Texture** for concrete
   - **ColorRamp** for weathering
   - **Mix RGB** to combine textures

### In Game Engines (Unity/Unreal):
1. Use triplanar mapping shader
2. Sample textures based on world position
3. Blend between materials based on surface normal

## Method 2: Baked Textures

For better performance:

1. **Improve UV mapping first** - Modify `generate_uvs()` in the script:
   ```python
   def generate_uvs(self, mesh):
       # Box projection per face
       faces = mesh.faces
       vertices = mesh.vertices
       uvs = np.zeros((len(vertices), 2))
       
       for face_idx, face in enumerate(faces):
           # Determine dominant axis of face
           normal = mesh.face_normals[face_idx]
           # Project based on normal direction
           # ... implement box projection
   ```

2. **Bake textures in Blender**:
   - Unwrap with Smart UV Project
   - Paint or generate textures
   - Bake to texture atlas

## Method 3: Vertex Colors

For very retro style:
```python
# Add to building_generator.py
def assign_vertex_colors(self, mesh):
    # Color by height (weathering)
    colors = np.ones((len(mesh.vertices), 4))
    z_values = mesh.vertices[:, 2]
    z_normalized = (z_values - z_values.min()) / (z_values.max() - z_values.min())
    
    # Darker at bottom (dirt), lighter at top
    colors[:, 0] = 0.6 + z_normalized * 0.3  # R
    colors[:, 1] = 0.6 + z_normalized * 0.3  # G
    colors[:, 2] = 0.6 + z_normalized * 0.3  # B
    
    mesh.visual.vertex_colors = colors
    return mesh
```

## Texture Ideas for Soviet Buildings

### Concrete Base
- Grey color (RGB: 120, 120, 115)
- Subtle noise for imperfections
- Darker at bottom (water damage)
- Panel lines every 2-3 floors

### Windows
- Dark blue/black for glass
- Slight reflection
- Random variations (curtains, lights)

### Balconies
- Slightly different color
- Rust stains on railings
- Random clutter

### Weathering
- Vertical water stains from roof
- Darker patches around windows
- Moss/dirt at base
- Random graffiti decals

## Retro Style Tips

For PS1/N64 aesthetic:
- Use 64x64 or 128x128 textures
- No filtering (point sampling)
- High contrast
- Vertex colors for cheap variation
- Bake ambient occlusion into vertices

## Material IDs

To export with material zones, modify the generator:
```python
# Assign different materials to:
# - Base (material 0)
# - Walls (material 1)  
# - Windows (material 2)
# - Roof (material 3)
# - Balconies (material 4)
```

This allows multi-texture materials in game engines.
