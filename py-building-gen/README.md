# Soviet-Style Apartment Building Generator

Procedurally generates low-poly 3D models of Soviet-style apartment blocks from pure code.

## Features

- **100% Procedural**: No hand-made assets - everything generated from code
- **Facade Variations**: Random but consistent patterns of windows, balconies, and double windows
- **Low-Poly**: Optimized for retro-style games
- **UV Mapped**: Ready for procedural texturing
- **Multiple Formats**: Exports to OBJ, GLB, and STL

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python building_generator.py
```

This generates a 5-story building with 4 apartments per floor.

## Customization

Edit the `main()` function to customize:

```python
# Change number of floors and apartments
building = generator.generate_building(num_floors=8, apartments_per_floor=6)

# Change seed for different variations
generator = BuildingGenerator(seed=123)

# Modify dimensions in __init__:
self.floor_height = 3.0          # Height of each floor
self.apartment_width = 4.0       # Width of each apartment unit
self.building_depth = 8.0        # Depth of building
self.window_width = 1.2          # Window dimensions
self.window_height = 1.5
```

## Architecture

The building consists of three main parts:

1. **Base**: Ground floor with entrance and varied windows
2. **Middle Floors**: Repeated floors with variant facades:
   - Variant 0: Simple window
   - Variant 1: Window with balcony
   - Variant 2: Double window
3. **Roof**: Flat roof with edge detail

## Output Files

- `soviet_apartment_block.obj` - Best for game engines (Unity, Unreal, Godot)
- `soviet_apartment_block.glb` - Modern format for web/3D viewers
- `soviet_apartment_block.stl` - For 3D printing or backup

## Next Steps

- Texture the models using the UV coordinates
- Add more facade variants (corner windows, shop fronts, etc.)
- Generate buildings with different footprints (L-shape, U-shape)
- Add weathering and damage to geometry
- Export with material IDs for multi-texture support

## License

Do whatever you want with it!
