# Getting Started with Facade Rectification

## Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Rectification Script
```bash
cd scripts
python facade_rectifier.py
```

### 3. How to Use the Interactive Tool

1. **The script will automatically convert your HEIC/DNG files to JPG format**
2. **For each image, you'll see a window where you need to click 4 corners:**
   - Click **Top-left** corner of the facade
   - Click **Top-right** corner of the facade  
   - Click **Bottom-right** corner of the facade
   - Click **Bottom-left** corner of the facade

3. **Controls:**
   - `Left Click`: Select corner point
   - `C`: Clear all selected corners and start over
   - `R`: Rectify the facade (after selecting 4 corners)
   - `Q`: Quit without processing

4. **The rectified images will be saved to `../rectified/` folder**

## Tips for Best Results

### Good Facade Photos:
- ✅ Camera roughly perpendicular to building face
- ✅ Minimal perspective distortion
- ✅ Clear, well-lit facades
- ✅ Facade fills most of the frame
- ✅ Sharp focus on building details

### Corner Selection Tips:
- **Be precise** - click exactly on building corners
- **Use architectural features** - window frames, building edges
- **Consistent depth** - all 4 corners should be on the same plane
- **Rectangular selection** - try to select a rectangular portion of the facade

### Common Issues:
- **Perspective too extreme**: Try photos taken from further away
- **3D elements**: Select corners on the main wall plane, ignoring balconies/fire escapes
- **Curved buildings**: This method works best on flat facades

## Next Steps

Once you have some rectified facades:

1. **Analyze the results** - check for distortion, quality
2. **Categorize by material type** (brick, concrete, metal, etc.)
3. **Extract repeating patterns** (window spacing, floor heights)
4. **Set up material classification system**
5. **Begin procedural generation experiments**

## File Structure After Processing
```
3d-building-generator/
├── pics-raw/           # Original HEIC/DNG files
├── pics-converted/     # Converted JPG files  
├── rectified/          # Rectified facade textures
│   ├── IMG_1711_rectified.png
│   ├── IMG_1711_homography.npy
│   └── ...
├── scripts/
│   └── facade_rectifier.py
└── doc.md
```

## Troubleshooting

**"pillow_heif not installed"**: 
```bash
pip install pillow_heif
```

**"Could not load image"**: 
- Check file paths
- Ensure image files aren't corrupted
- Try converting manually first

**"Rectification looks distorted"**:
- Reselect corners more precisely
- Ensure facade is roughly rectangular in photo
- Try a different photo with less perspective distortion
