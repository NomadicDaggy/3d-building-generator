"""
Example script showing different building configurations
"""

from building_generator import BuildingGenerator


def generate_variety():
    """Generate multiple building variations"""
    
    # Small building - 3 stories, narrow
    print("\n=== Generating small building ===")
    small_gen = BuildingGenerator(seed=1)
    small_gen.floor_height = 2.8
    small_gen.apartment_width = 3.5
    small = small_gen.generate_building(num_floors=3, apartments_per_floor=3)
    small.export('building_small.obj')
    print("✓ Saved building_small.obj")
    
    # Large building - 9 stories, wide
    print("\n=== Generating large building ===")
    large_gen = BuildingGenerator(seed=2)
    large = large_gen.generate_building(num_floors=9, apartments_per_floor=6)
    large.export('building_large.obj')
    print("✓ Saved building_large.obj")
    
    # Tall thin building
    print("\n=== Generating tall thin building ===")
    tall_gen = BuildingGenerator(seed=3)
    tall_gen.building_depth = 6.0
    tall = tall_gen.generate_building(num_floors=12, apartments_per_floor=2)
    tall.export('building_tall.obj')
    print("✓ Saved building_tall.obj")
    
    # Wide short building
    print("\n=== Generating wide short building ===")
    wide_gen = BuildingGenerator(seed=4)
    wide_gen.floor_height = 3.2
    wide = wide_gen.generate_building(num_floors=4, apartments_per_floor=8)
    wide.export('building_wide.obj')
    print("✓ Saved building_wide.obj")
    
    print("\n✅ Generated 4 building variations!")


if __name__ == "__main__":
    generate_variety()
