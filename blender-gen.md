# Blender-Based 3D Building Generator Architecture

## Overview

This document outlines the complete architecture for a Blender-based procedural building generator that serves 3D models to games. The system uses Blender's powerful geometry operations and Python scripting to create buildings on-demand.

## Architecture Diagram

```
Game Engine          Blender Service         File System
    |                      |                     |
    | HTTP Request         |                     |
    |--------------------->|                     |
    |  BuildingParams      |                     |
    |                      |---> Generate        |
    |                      |     Building        |
    |                      |                     |
    |                      |---> Export -------->| building_123.fbx
    |                      |     FBX/glTF        |
    |                      |                     |
    | Response             |                     |
    |<---------------------|                     |
    |  {file_path}         |                     |
    |                      |                     |
    | Load Model           |                     |
    |------------------------------------->      |
```

## Development Architecture

### Phase 1: Visual Development (Blender GUI)

**Purpose**: Develop and test building generation rules visually

**Workflow**:
1. Open Blender with custom building generation addon
2. Adjust parameters in custom panel
3. Generate building in 3D viewport
4. Iterate on rules and geometry
5. Test materials and export formats

**File Structure**:
```
blender-building-gen/
├── addons/
│   └── building_generator/
│       ├── __init__.py              # Blender addon registration
│       ├── ui_panel.py              # Custom UI panel
│       ├── building_core.py         # Core building generation
│       ├── architectural_rules.py   # Rule definitions
│       └── material_system.py       # Material assignment
├── rules/
│   ├── residential.json            # Building type rules
│   ├── commercial.json
│   └── industrial.json
├── materials/
│   └── building_materials.blend    # Material library
└── test_buildings/
    └── generated/                   # Test outputs
```

### Phase 2: Production Service (Blender Headless)

**Purpose**: HTTP service that generates buildings on-demand

**Technology Stack**:
- **Blender Python API**: Building generation
- **Flask/FastAPI**: HTTP service layer
- **Docker**: Containerized deployment
- **JSON**: Parameter configuration

## Implementation Details

### 1. Core Building Generator Module

```python
# building_core.py
import bpy
import bmesh
import json
from mathutils import Vector

class BuildingGenerator:
    def __init__(self, rules_path="rules/"):
        self.rules = self.load_rules(rules_path)
        
    def generate_building(self, params):
        """
        Main generation function
        params: {
            'width': float,
            'depth': float, 
            'height': float,
            'floors': int,
            'style': str,  # 'residential', 'commercial', 'industrial'
            'seed': int
        }
        """
        self.clear_scene()
        
        # Get style rules
        style_rules = self.rules[params['style']]
        
        # Generate base structure
        building_mesh = self.create_base_structure(params)
        
        # Apply facade system
        self.apply_facade_grid(building_mesh, params, style_rules)
        
        # Add architectural details
        self.add_windows_and_doors(building_mesh, params, style_rules)
        self.add_balconies(building_mesh, params, style_rules)
        self.add_roof_details(building_mesh, params, style_rules)
        
        # Apply materials
        self.apply_materials(building_mesh, style_rules)
        
        return building_mesh
```

### 2. Architectural Rules System

```json
// rules/residential.json
{
    "name": "residential",
    "facade_grid": {
        "window_spacing": {"min": 1.5, "max": 3.0},
        "floor_height": 3.0,
        "window_size": {"width": 1.2, "height": 1.5}
    },
    "probabilities": {
        "window_per_bay": 0.8,
        "balcony_per_window": 0.3,
        "ac_unit_per_window": 0.4,
        "door_ground_floor": 0.2
    },
    "materials": {
        "wall_primary": "brick_red",
        "window_frame": "metal_white",
        "door": "wood_brown",
        "balcony": "concrete_gray"
    },
    "details": {
        "base_height": 0.3,
        "roof_overhang": 0.2,
        "window_sill_depth": 0.1,
        "balcony_depth": 1.2
    }
}
```

### 3. HTTP Service Layer

```python
# building_service.py
from flask import Flask, request, jsonify, send_file
import bpy
import os
import uuid
from building_core import BuildingGenerator

app = Flask(__name__)
generator = BuildingGenerator()

@app.route('/generate_building', methods=['POST'])
def generate_building():
    try:
        params = request.json
        
        # Generate unique ID for this building
        building_id = str(uuid.uuid4())
        params['id'] = building_id
        
        # Generate building in Blender
        building_mesh = generator.generate_building(params)
        
        # Export to file
        export_path = f"output/building_{building_id}"
        export_formats = params.get('formats', ['fbx'])
        
        exported_files = {}
        for format_type in export_formats:
            file_path = f"{export_path}.{format_type}"
            
            if format_type == 'fbx':
                bpy.ops.export_scene.fbx(
                    filepath=file_path,
                    use_selection=True,
                    object_types={'MESH'}
                )
            elif format_type == 'gltf':
                bpy.ops.export_scene.gltf(
                    filepath=file_path,
                    use_selection=True
                )
            
            exported_files[format_type] = file_path
        
        return jsonify({
            "status": "success",
            "building_id": building_id,
            "files": exported_files,
            "download_url": f"/download/{building_id}"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download/<building_id>')
def download_building(building_id):
    file_path = f"output/building_{building_id}.fbx"
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # Run Blender with this script
    app.run(host='0.0.0.0', port=5000)
```

### 4. Game Engine Integration

#### Unity Example:
```csharp
// BuildingService.cs
using UnityEngine;
using UnityEngine.Networking;
using System.Threading.Tasks;

public class BuildingService : MonoBehaviour
{
    [System.Serializable]
    public class BuildingParams
    {
        public float width = 10f;
        public float depth = 15f;
        public float height = 20f;
        public int floors = 6;
        public string style = "residential";
        public int seed = 12345;
        public string[] formats = {"fbx"};
    }
    
    [System.Serializable]
    public class BuildingResponse
    {
        public string status;
        public string building_id;
        public string download_url;
    }
    
    private string serviceUrl = "http://localhost:5000";
    
    public async Task<GameObject> GenerateBuilding(BuildingParams buildingParams)
    {
        // Send request to Blender service
        string json = JsonUtility.ToJson(buildingParams);
        
        using (UnityWebRequest request = UnityWebRequest.Post($"{serviceUrl}/generate_building", json, "application/json"))
        {
            await request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                BuildingResponse response = JsonUtility.FromJson<BuildingResponse>(request.downloadHandler.text);
                
                // Download the generated building
                return await DownloadBuilding(response.download_url);
            }
        }
        
        return null;
    }
    
    private async Task<GameObject> DownloadBuilding(string downloadUrl)
    {
        // Download and import the FBX file
        using (UnityWebRequest request = UnityWebRequest.Get($"{serviceUrl}{downloadUrl}"))
        {
            await request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                // Save to temporary file and import
                string tempPath = Application.temporaryCachePath + "/temp_building.fbx";
                System.IO.File.WriteAllBytes(tempPath, request.downloadHandler.data);
                
                // Import using Unity's model importer
                // (Implementation depends on your asset import pipeline)
                return ImportFBXAsGameObject(tempPath);
            }
        }
        
        return null;
    }
}
```

## Deployment Options

### Option 1: Local Development Server
```bash
# Start Blender with service
blender --background --python building_service.py
```

### Option 2: Docker Container
```dockerfile
# Dockerfile
FROM ubuntu:20.04

# Install Blender
RUN apt-get update && apt-get install -y \
    blender \
    python3-pip

# Copy service files
COPY building_service.py /app/
COPY building_core.py /app/
COPY rules/ /app/rules/

WORKDIR /app
EXPOSE 5000

CMD ["blender", "--background", "--python", "building_service.py"]
```

### Option 3: Cloud Function (Advanced)
- Deploy as AWS Lambda or Google Cloud Function
- Use headless Blender in container
- Store generated models in cloud storage

## Performance Optimizations

### 1. Caching Strategy
```python
class BuildingCache:
    def __init__(self):
        self.cache = {}
    
    def get_building(self, params_hash):
        if params_hash in self.cache:
            return self.cache[params_hash]
        return None
    
    def store_building(self, params_hash, file_path):
        self.cache[params_hash] = file_path
```

### 2. LOD Generation
```python
def generate_building_with_lod(params, lod_level):
    if lod_level == 0:  # High detail
        detail_params = params
    elif lod_level == 1:  # Medium detail
        detail_params = reduce_detail(params, 0.5)
    else:  # Low detail (distant)
        detail_params = create_simple_box(params)
    
    return generate_building(detail_params)
```

### 3. Batch Processing
```python
@app.route('/generate_batch', methods=['POST'])
def generate_building_batch():
    building_list = request.json['buildings']
    results = []
    
    for building_params in building_list:
        result = generator.generate_building(building_params)
        results.append(result)
    
    return jsonify({"buildings": results})
```

## Development Workflow

### Phase 1: Setup & Testing (Week 1)
1. Create Blender addon with basic UI
2. Implement simple box generation
3. Test export pipeline to Unity/Godot
4. Set up Flask service skeleton

### Phase 2: Core Building System (Week 2)
1. Implement facade grid system
2. Add window and door placement
3. Create material assignment system
4. Test with multiple building styles

### Phase 3: Architectural Details (Week 3)
1. Add balcony generation
2. Implement roof details
3. Add building services (AC units, etc.)
4. Create variation system

### Phase 4: Production Ready (Week 4)
1. Optimize performance
2. Add caching system
3. Create Docker deployment
4. Implement batch processing

## File Management

### Directory Structure:
```
/output/
├── buildings/
│   ├── building_uuid1.fbx
│   ├── building_uuid1.gltf
│   └── building_uuid2.fbx
├── cache/
│   └── [cached buildings by hash]
└── temp/
    └── [temporary files]
```

### Cleanup Strategy:
```python
import schedule
import time

def cleanup_old_files():
    # Remove files older than 24 hours
    cleanup_directory("output/buildings", max_age_hours=24)
    cleanup_directory("output/temp", max_age_hours=1)

schedule.every().hour.do(cleanup_old_files)
```

## Advantages of This Architecture

1. **Visual Development**: See buildings as you create them
2. **Powerful Geometry**: Leverage Blender's mesh operations
3. **Game Engine Agnostic**: Works with Unity, Godot, Unreal, etc.
4. **Scalable**: Can run on local machine or cloud
5. **Material System**: Built-in PBR materials
6. **Export Flexibility**: Multiple formats (FBX, glTF, OBJ)
7. **Iteration Speed**: Quick rule changes and testing

## Next Steps

1. Create basic Blender addon structure
2. Implement simple building generator
3. Set up Flask service
4. Test with Unity integration
5. Expand architectural rules system

This architecture provides a solid foundation for procedural building generation that can scale from prototype to production city generation.
