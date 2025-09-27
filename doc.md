# 3D Building Generator: Facade Rectification Pipeline

## Overview

This document outlines a complete pipeline for converting real-world building facade photographs into a procedural building generator for games. The target aesthetic is gritty, low-resolution textures with realistic lighting (PS1/PS2 era visual style with modern lighting).

## Core Concept

**Goal**: Create a procedural building system that generates realistic urban environments using rectified photo textures and extracted architectural patterns.

**Approach**: Photo capture → Rectification → Pattern extraction → Procedural generation → City assembly

## Phase 1: Facade Rectification

### What is Facade Rectification?
Converting perspective photographs of building facades into orthographic (straight-on) projections suitable for texturing 3D models.

### Standard Methods

**1. Homographic Transformation (Recommended)**
- Uses perspective transformation matrix (homography)
- Requires 4+ corresponding points between perspective and orthographic views
- Best when camera is roughly perpendicular to facade

**2. Vanishing Point Method**
- Detects vanishing points from parallel lines
- More robust for angled photographs
- Better for complex perspective corrections

### Technical Implementation
- **OpenCV + Python**: `findHomography()` and `warpPerspective()` functions
- **Alternative tools**: Photoshop perspective correction, Blender reference plane modeling
- **Workflow**: Mark corner points → Define target rectangle → Apply transformation → Crop to tiles

## Phase 2: Handling 3D Features

### The Challenge
Balconies, fire escapes, window ledges, and other 3D elements break the flat facade assumption of simple rectification.

### Solutions

**1. Layer Separation Approach (Recommended)**
- Rectify base wall ignoring 3D features
- Extract 3D elements as separate textures/alpha masks
- Create depth layers: base wall + floating detail elements
- Generate geometry with proper Z-offsets

**2. Multiple Plane Rectification**
- Identify different depth planes (wall, balcony face, underside)
- Rectify each plane separately
- Recombine in 3D space during generation

**3. Hybrid Geometry + Texture**
- Rectified textures for flat surfaces
- Simple box geometry for major 3D features
- Material layering system for different components

## Phase 3: Material Properties & Lighting

### Material Classification System
Each rectified texture needs material type assignment for proper lighting response.

**Material Types & Properties:**
- **Brick**: Roughness 0.8, Metallic 0.0, High normal intensity
- **Concrete**: Roughness 0.7, Metallic 0.0, Low normal intensity  
- **Painted Metal**: Roughness 0.3, Metallic 0.8, Medium normal intensity
- **Weathered Metal**: Roughness 0.9, Metallic 0.6, High normal intensity
- **Glass**: Roughness 0.1, Metallic 0.0, Reflection enabled

### Supporting Map Generation
- **Normal Maps**: Auto-generate from albedo using Materialize or Substance Designer
- **Roughness Maps**: Extract from brightness variations or manual painting
- **Metallic Masks**: Simple black/white masks for metal vs non-metal surfaces

## Phase 4: Full Pipeline Architecture

### Data Acquisition & Processing
1. **Photo Capture**
   - Facade photos with reference measurements
   - Multiple angles and lighting conditions
   - Overlap for larger buildings

2. **Rectification Processing**
   - OpenCV/Python rectification pipeline
   - Output to standardized tile sizes (256x256, 512x512)
   - Categorize by material type, style, condition

3. **Texture Atlas Creation**
   - Organize by building archetypes
   - Create variation sets for each material type

### Pattern Extraction & Rule Definition
1. **Architectural Analysis**
   - Extract window spacing, floor heights, proportions
   - Define building archetypes: residential, commercial, industrial
   - Document variation parameters and material combinations

2. **Building DNA Database**
   - Store architectural rules and constraints
   - Material assignment rules (base/middle/top combinations)
   - Damage/wear pattern locations and types

### Procedural Building Generator
1. **Geometry Generation**
   - **Tools**: Blender + Python or Houdini
   - Generate based on archetype rules
   - Apply rectified textures via UV mapping
   - Add procedural wear/damage overlays

2. **Export Pipeline**
   - Prefab meshes with texture variants
   - LOD versions for performance
   - Material property assignments

### City Generation System
1. **Layout Generation**
   - **Recommended Engine**: Unity (better procedural ecosystem)
   - **Alternative**: Godot 4 (budget-friendly)
   - Street/lot generation using L-systems
   - Building placement with zoning rules

2. **Runtime Systems**
   - Asset streaming for large cities
   - Runtime texture variation
   - Performance optimization (culling, batching)

## Phase 5: Engine Implementation

### Unity Approach
- **Universal Render Pipeline** for modern lighting
- Custom material system with texture arrays
- Material presets for different surface types
- Vertex color mixing for wear variation

### Godot 4 Approach
- **StandardMaterial3D** workflow
- Material resource files for surface types
- Built-in roughness/metallic pipeline
- Performance-focused batching

## Key Tools Pipeline

```
Photos → OpenCV/Python → Substance Designer → Blender/Houdini → Unity/Godot
```

**Primary Tools:**
- **Rectification**: OpenCV + Python
- **Material Processing**: Substance Designer
- **Procedural Generation**: Blender + Python scripting
- **Game Engine**: Unity (recommended) or Godot 4
- **Supporting**: Materialize (normal maps), custom scripts

## Technical Considerations

### Performance Optimization
- Texture atlasing for efficient batching
- LOD system for different viewing distances
- Culling systems for large cities
- Asset streaming for memory management

### Visual Quality
- Low-resolution textures (256x256 base) for retro aesthetic
- Realistic material properties for authentic lighting
- Procedural wear/damage for visual variety
- Compression artifacts enhance retro feel

### Scalability
- Modular texture system allows easy expansion
- Rule-based generation scales to any city size
- Material classification system works with any photo input
- Procedural approach reduces manual art asset requirements

## Benefits of This Approach

1. **Authentic Materials**: Real-world weathering, dirt, and wear patterns
2. **Scalable Content**: One rectified facade becomes multiple building variations
3. **Efficient Pipeline**: Leverages programming skills over artistic requirements
4. **Flexible System**: Easy to add new building types and materials
5. **Performance Friendly**: Optimized for batch rendering and large-scale cities
6. **Realistic Lighting**: Proper material properties create convincing lighting response
