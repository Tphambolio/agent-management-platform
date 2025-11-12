# Fuel Layer Visualization Research Report

**Generated**: 2025-10-29 08:50:45
**Papers Analyzed**: 200
**Actionable Insights**: 2

---

## Executive Summary

Research into visualizing wildfire fuel layers and fire-vegetation interactions.

### Key Findings

**Top Recommendation Categories:**
- Fuel Layer Overlay: 1 papers
- Performance: 1 papers

**Research Gap Identified:**
Current visualizations show fire probability and intensity, but lack connection to
actual fuel layers (trees, grass, shrubs). Users cannot see:
- What fuel types exist in the landscape
- How fire spreads through different vegetation
- Before/after fuel consumption
- Vertical fuel structure (ground → ladder → crown)

---

## High-Priority Recommendations

### 1. Fuel layer overlay

**Description**: Overlay fuel types on fire probability maps

**Impact**: Connect fire to vegetation

**Priority**: HIGH

**Source**: Raster Forge: Interactive Raster Manipulation Library and GUI for Python...

### 2. GPU instancing for vegetation

**Description**: Use GPU instancing to render thousands of trees

**Impact**: Render large forests efficiently

**Priority**: HIGH

**Source**: Using efficient parallelization in Graphic Processing Units to
  parameterize stochastic fire propag...


---

## Technology Stack for Fuel Visualization

**Recommended Approaches:**

### 1. Fuel Layer Overlay (Quick Win - Week 1)
- **What**: Overlay fuel type map on fire probability heatmap
- **How**: Semi-transparent layer showing C1-C7, O1a/b, S1-S3 fuel codes
- **Benefit**: Immediate connection between fire and vegetation
- **Difficulty**: Low (use existing fuel maps)

### 2. 3D Vegetation Rendering (Medium - Week 2-3)
- **What**: Render actual trees and grass in 3D using Three.js
- **How**: Use procedural tree generation + GPU instancing
- **Benefit**: Realistic visualization of what's actually burning
- **Difficulty**: Medium (Three.js + shaders)

### 3. Fuel Consumption Animation (Advanced - Week 4)
- **What**: Animate fuel being consumed as fire spreads
- **How**: Reduce vegetation opacity/color as cells burn
- **Benefit**: Show fire-fuel interaction in real-time
- **Difficulty**: Medium-High (temporal state tracking)

### 4. Vertical Fuel Structure (Advanced - Week 5)
- **What**: Show ground fuels, ladder fuels, crown fuels in layers
- **How**: Multi-layer 3D rendering with height-based coloring
- **Benefit**: Explain crown fire transitions
- **Difficulty**: High (3D scene management)

---

## Detailed Paper Analysis

### Paper 1: A wildland fire modeling and visualization environment

**Relevance Score**: 0.30
**URL**: http://arxiv.org/abs/1111.4610v1
**Keywords**: fuel map

---

### Paper 2: A wildland fire modeling and visualization environment

**Relevance Score**: 0.30
**URL**: http://arxiv.org/abs/1111.4610v1
**Keywords**: fuel map

---

### Paper 3: A wildland fire modeling and visualization environment

**Relevance Score**: 0.30
**URL**: http://arxiv.org/abs/1111.4610v1
**Keywords**: fuel map

---

### Paper 4: A wildland fire modeling and visualization environment

**Relevance Score**: 0.30
**URL**: http://arxiv.org/abs/1111.4610v1
**Keywords**: fuel map

---

### Paper 5: Wildfire fuel mapping using airborne laser scanning data: Climate adaptation planning with the Xáxli’p community

**Relevance Score**: 0.30
**URL**: https://doi.org/10.24124/2025/30526
**Keywords**: fuel map

---

### Paper 6: Using efficient parallelization in Graphic Processing Units to
  parameterize stochastic fire propagation models

**Relevance Score**: 0.25
**URL**: http://arxiv.org/abs/1701.03549v2
**Keywords**: lod

---

### Paper 7: Pan-European fuel map server: an open-geodata portal for supporting fire
  risk assessment

**Relevance Score**: 0.25
**URL**: http://arxiv.org/abs/2409.00008v1
**Keywords**: surface fuel, fuel map, fuel model

---

### Paper 8: Using efficient parallelization in Graphic Processing Units to
  parameterize stochastic fire propagation models

**Relevance Score**: 0.25
**URL**: http://arxiv.org/abs/1701.03549v2
**Keywords**: lod

---

### Paper 9: FUELVISION: A Multimodal Data Fusion and Multimodel Ensemble Algorithm
  for Wildfire Fuels Mapping

**Relevance Score**: 0.25
**URL**: http://arxiv.org/abs/2403.15462v1
**Keywords**: fuel map, fuel type

---

### Paper 10: Raster Forge: Interactive Raster Manipulation Library and GUI for Python

**Relevance Score**: 0.20
**URL**: http://arxiv.org/abs/2404.06389v2
**Keywords**: fuel map

---

### Paper 11: A review of machine learning applications in wildfire science and
  management

**Relevance Score**: 0.20
**URL**: http://arxiv.org/abs/2003.00646v2
**Keywords**: 

---

### Paper 12: Fire responses shape plant communities in a minimal model for fire
  ecosystems across the world

**Relevance Score**: 0.20
**URL**: http://arxiv.org/abs/2304.06445v1
**Keywords**: 

---

### Paper 13: FIRETWIN: Digital Twin Advancing Multi-Modal Sensing, Interactive
  Analytics for Wildfire Response

**Relevance Score**: 0.20
**URL**: http://arxiv.org/abs/2510.18879v1
**Keywords**: 

---

### Paper 14: Dual-Task Learning for Dead Tree Detection and Segmentation with Hybrid
  Self-Attention U-Nets in Aerial Imagery

**Relevance Score**: 0.20
**URL**: http://arxiv.org/abs/2503.21438v1
**Keywords**: 

---

### Paper 15: Holocene fire regimes around the Altai-Sayan Mountains and adjacent plains: interaction with climate and vegetation types

**Relevance Score**: 0.20
**URL**: https://doi.org/10.5194/egusphere-2025-1991
**Keywords**: surface fire

---


---

## Implementation Roadmap

### Phase 1: Fuel Layer Integration (Week 1) - QUICK WIN

**Goal**: Connect fire visualizations to actual fuel data

1. **Fuel Map Overlay**
   - Read Canadian FBP fuel type from rasters
   - Create color-coded fuel type layer
   - Overlay on burn probability map with 50% transparency
   - Legend: C1-C7 (green shades), O1a/b (tan), S1-S3 (brown), D1-D2 (gray)

2. **Fuel-Fire Alignment Check**
   - Show fuel type at each burning cell
   - Highlight mismatches (fire in non-burnable fuel)
   - Display fuel-specific ROS in popup

3. **Code Changes**:
   ```python
   # Add to WebGLFireVisualizer
   def add_fuel_layer(self, fuel_map: np.ndarray, ...):
       # Render fuel types as colored overlay
       # Use FBP color scheme
   ```

**Expected Output**: Fire heatmap with visible fuel types underneath

---

### Phase 2: 3D Vegetation (Week 2-3) - MEDIUM DIFFICULTY

**Goal**: Render actual trees/grass in 3D

1. **Procedural Tree Generation**
   - Use Three.js for WebGL rendering
   - Generate simple tree models (cylinders + spheres)
   - Different models for conifer (C1-C7) vs deciduous (D1-D2)
   - Grass billboards for O1a/b

2. **GPU Instancing**
   - Render 10,000+ trees using GPU instancing
   - LOD system: detailed trees near camera, billboards far away
   - Frustum culling for performance

3. **Integration with Fire**
   - Color trees based on burn probability
   - Animate tree burning (color change, particle effects)

**Technology**: Three.js + WebGL shaders

---

### Phase 3: Advanced Features (Week 4-5) - OPTIONAL

1. **Fuel Consumption Animation**
2. **Vertical Fuel Structure**
3. **Before/After Comparison**

---

## Code Examples

### Example 1: Fuel Type Overlay
```python
def create_fuel_fire_overlay(burn_prob, fuel_map, bbox):
    viz = WebGLFireVisualizer()

    # Create two layers
    fire_layer = viz.create_gpu_heatmap(burn_prob, bbox)
    fuel_layer = viz.add_fuel_type_layer(fuel_map, bbox, opacity=0.5)

    # Combine in single view
    return viz.create_combined_view([fire_layer, fuel_layer])
```

### Example 2: 3D Forest Rendering (Three.js)
```javascript
// Generate conifer trees for C2 fuel type
function generateConiferForest(fuelMap, rows, cols) {
    const trees = [];

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (fuelMap[r][c] === 'C2') {  // Jack Pine fuel
                // Create simple conifer
                const trunk = new THREE.CylinderGeometry(0.1, 0.15, 3);
                const crown = new THREE.ConeGeometry(0.8, 4, 8);

                const tree = new THREE.Group();
                tree.add(new THREE.Mesh(trunk, trunkMaterial));
                tree.add(new THREE.Mesh(crown, crownMaterial));

                tree.position.set(c * 30, 0, r * 30);  // 30m spacing
                trees.push(tree);
            }
        }
    }

    return trees;
}
```

---

## Key Insights from Literature

- **A wildland fire modeling and visualization environment...**: fuel map
- **A wildland fire modeling and visualization environment...**: fuel map
- **A wildland fire modeling and visualization environment...**: fuel map
- **A wildland fire modeling and visualization environment...**: fuel map
- **Wildfire fuel mapping using airborne laser scanning data: Climate adaptation pla...**: fuel map
- **Using efficient parallelization in Graphic Processing Units to
  parameterize st...**: lod
- **Pan-European fuel map server: an open-geodata portal for supporting fire
  risk ...**: surface fuel, fuel map, fuel model
- **Using efficient parallelization in Graphic Processing Units to
  parameterize st...**: lod
- **FUELVISION: A Multimodal Data Fusion and Multimodel Ensemble Algorithm
  for Wil...**: fuel map, fuel type
- **Raster Forge: Interactive Raster Manipulation Library and GUI for Python...**: fuel map

---

## Gaps and Opportunities

### Current Gap:
Fire visualizations are **abstract heatmaps** disconnected from physical fuel.

### Opportunity:
Show fire interacting with **actual vegetation** (trees, grass, shrubs).

### Impact:
- **Educational**: Users see what's actually burning
- **Intuitive**: Connection between fire and landscape
- **Scientific**: Validate fuel-fire relationships
- **Operational**: Better communication with stakeholders

---

## Next Steps

1. **Implement Phase 1** (Fuel Layer Overlay) - 1 week
2. **Test with Edmonton scenario** - Verify C2 fuels align with fire spread
3. **Gather user feedback** - Do users understand fuel-fire connection?
4. **Plan Phase 2** (3D vegetation) if Phase 1 successful

---

## References

Total papers analyzed: 200
Top sources: arXiv (140),
             CrossRef (60)

**Generated by**: Professor Fuel Visualization Researcher
**Focus**: Connecting fire visualization to actual fuel layers
**Priority**: HIGH - Critical gap in current system

