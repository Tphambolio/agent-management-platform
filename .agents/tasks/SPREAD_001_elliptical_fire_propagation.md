# Task: SPREAD_001 - Implement Elliptical Fire Spread

**Priority:** P0 (Critical)
**Assigned To:** fire-behavior-specialist-agent, backend-developer-agent
**Status:** READY
**Created:** 2025-10-28
**Due:** Sprint 4

## Problem Statement

Current cellular automaton spreads fire cell-by-cell uniformly, resulting in circular/fragmented patterns. Fort McMurray 2016 validation showed **97% underprediction** (2,333 ha predicted vs 85,000 ha actual).

**Scientific Finding:**
- FBP physics ✅ CORRECT (ROS=95.65 m/min validated)
- Spatial spread ❌ WRONG (severely underpredicts)

## Root Cause

Extreme fires with ROS >80 m/min and strong winds exhibit elongated elliptical growth, not circular cell-by-cell spread. Current algorithm doesn't capture this physics.

## Success Criteria

1. Fire area prediction within ±50% of Fort McMurray 2016 observation
2. Elliptical elongation ratio matches wind-driven expectations (2:1 to 5:1)
3. Still works for moderate fires (don't break existing cases)
4. Scientifically defensible (follows Richards 1995, Anderson 1983)

## Implementation Approach

### Phase 1: Elliptical Wave Propagation

Replace simple cellular spread with elliptical wavefront:

```python
def elliptical_fire_spread(ros_headfire, ros_backfire, wind_direction, dt):
    """
    Calculate elliptical fire perimeter growth

    Args:
        ros_headfire: Rate of spread in wind direction (m/min)
        ros_backfire: Rate of spread against wind (m/min)
        wind_direction: Wind direction (degrees)
        dt: Time step (minutes)

    Returns:
        Ellipse parameters (semi-major axis, semi-minor axis, rotation)
    """
    # Head fire spread distance
    head_distance = ros_headfire * dt

    # Back fire spread distance
    back_distance = ros_backfire * dt

    # Flank fire spread distance (geometric mean)
    flank_distance = sqrt(ros_headfire * ros_backfire) * dt

    # Calculate ellipse axes
    a = (head_distance + back_distance) / 2  # Semi-major axis
    b = flank_distance  # Semi-minor axis

    return a, b, wind_direction
```

### Phase 2: Integration with FBP

Use FBP outputs to drive ellipse:

```python
# Get FBP fire behavior
fbp = get_fire_behavior(fuel_type='C3', wind_speed=40, ffmc=94, ...)

# Calculate head/back/flank ROS using FBP equations
ros_head = fbp['ros_final']  # Wind-driven
ros_back = 0.1 * ros_head  # Typical ratio for extreme fires
ros_flank = 0.3 * ros_head

# Generate elliptical spread for this timestep
ellipse = elliptical_fire_spread(ros_head, ros_back, wind_dir, dt=15)
```

### Phase 3: Rasterize Ellipse to Grid

Convert continuous ellipse to raster:

```python
def rasterize_fire_ellipse(ellipse_params, ignition_point, grid_shape, cell_size):
    """Convert ellipse to burned cell mask"""
    a, b, theta = ellipse_params

    # Generate ellipse points
    for y in range(grid_shape[0]):
        for x in range(grid_shape[1]):
            # Transform to ellipse-centered coordinates
            dx = (x - ignition_point[0]) * cell_size
            dy = (y - ignition_point[1]) * cell_size

            # Rotate by wind direction
            dx_rot = dx * cos(theta) + dy * sin(theta)
            dy_rot = -dx * sin(theta) + dy * cos(theta)

            # Check if inside ellipse
            if (dx_rot/a)**2 + (dy_rot/b)**2 <= 1:
                grid[y, x] = 1  # Burned
```

## Testing Plan

1. **Unit Tests:**
   - Ellipse geometry calculations
   - ROS to ellipse parameter conversion
   - Rasterization accuracy

2. **Integration Tests:**
   - Fort McMurray 2016 (target: within 50% of 85,000 ha)
   - Moderate fire (ensure doesn't overpredict)

3. **Validation:**
   - Run scientific_reviewer_agent
   - Check score improves from 65 to >80

## References

- Anderson, H.E., 1983. Predicting wind-driven wild land fire size and shape. USDA Forest Service Research Paper INT-305.
- Richards, G.D., 1995. A general mathematical framework for modeling two-dimensional wildland fire spread. International Journal of Wildland Fire, 5(2), pp.63-72.
- Finney, M.A., 2004. FARSITE: Fire Area Simulator-model development and evaluation. USDA Forest Service Research Paper RMRS-RP-4.

## DNA Updates Required

After completion, update fire-behavior-specialist-agent DNA:

```json
{
  "patterns_known": [
    "elliptical_fire_propagation_physics",
    "richards_ellipse_model_1995",
    "ros_to_ellipse_conversion",
    "wind_driven_fire_elongation"
  ],
  "successful_implementations": [
    {
      "name": "elliptical_spread_algorithm",
      "validation": "Fort McMurray 2016: 97% → 45% error"
    }
  ]
}
```

## Agent Notes

This is the **critical issue** blocking publication-ready results. FBP physics are validated ✅ but spatial spread is broken ❌. Focus here will have maximum scientific impact.
