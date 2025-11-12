# Task: SPREAD_002 - Dynamic Iteration Scaling

**Priority:** P1 (High)
**Assigned To:** backend-developer-agent
**Status:** READY
**Created:** 2025-10-28
**Effort:** Low (1-2 hours)

## Problem

Fixed 80 iterations inadequate for extreme fires. Fort McMurray with ROS=95 m/min needs ~180 iterations to simulate 30 hours.

## Solution

Calculate required iterations dynamically:

```python
def calculate_required_iterations(ros_mmin, duration_hours, cell_size_m, target_coverage=0.8):
    """
    Calculate iterations needed for fire to spread across domain

    Args:
        ros_mmin: Rate of spread (m/min)
        duration_hours: Simulation duration (hours)
        cell_size_m: Grid cell size (meters)
        target_coverage: Fraction of potential spread to simulate

    Returns:
        Number of iterations required
    """
    # Total distance fire could travel
    max_distance_m = ros_mmin * 60 * duration_hours

    # Cells to traverse
    cells_to_traverse = max_distance_m / cell_size_m

    # Iterations needed (assume 1-3 cells per iteration)
    iterations = int(cells_to_traverse * target_coverage / 2)

    # Bounds check
    iterations = max(50, min(iterations, 500))

    return iterations
```

## Implementation

Update `fire_model_agent.py`:

```python
# After FBP calculation
ros = fbp_result['ros_final']
required_iters = calculate_required_iterations(
    ros_mmin=ros,
    duration_hours=30,  # Or from config
    cell_size_m=30.0
)

print(f"📊 Calculated {required_iters} iterations for ROS={ros:.1f} m/min")

MAX_ITERATIONS = required_iters  # Use calculated value
```

## Expected Impact

Fort McMurray: Will allow fire to spread to observed extent (currently stops after 80 iterations)

## DNA Update

```json
{
  "patterns_known": ["dynamic_iteration_scaling"],
  "implementations": ["ros_based_iteration_calculation"]
}
```
