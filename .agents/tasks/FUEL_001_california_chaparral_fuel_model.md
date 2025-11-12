# Task: FUEL_001 - California Chaparral Fuel Model

**Priority:** P2 (High - Ecosystem Expansion)
**Assigned To:** fire-behavior-specialist-agent
**Status:** READY
**Created:** 2025-10-28
**Effort:** High (2-4 weeks)

## Problem

Canadian FBP system does not include California chaparral shrublands. Using C7 (Ponderosa Pine) as analog results in 109% overprediction for Palisades Fire 2025.

## Scientific Basis

California chaparral has fundamentally different fire behavior:
- **Fuel structure:** Dense shrubs 1-4m tall, not trees
- **Fuel loading:** 20-40 tonnes/ha of fine fuels
- **Fire intensity:** 10,000-50,000 kW/m (similar to crown fires)
- **Spread rate:** Highly wind-driven, 20-100 m/min under Santa Ana
- **Fire type:** Surface fire but high intensity (not crown fire)

## Evidence from Validation

**Palisades Fire 2025:**
- Actual: 6,879 ha (24 hours)
- C7 Prediction: 14,376 ha (109% overprediction)
- C7 ROS: 22.11 m/min (likely too low for chaparral)
- Conditions: FFMC=97, Wind=130 km/h, FWI=60

## Solution

Create custom fuel type "CH1" (California Chaparral) based on empirical data:

### Step 1: Research Existing Models

Review published chaparral fire behavior:
- Rothermel fuel model 4 (chaparral)
- FARSITE chaparral fuel types
- California Fire Lab empirical studies
- Camp Fire, Thomas Fire, Tubbs Fire documentation

### Step 2: Define CH1 Fuel Parameters

```python
# Proposed CH1 fuel type
FUEL_CHAPARRAL = {
    'code': 'CH1',
    'name': 'California Chaparral',
    'fuel_load': {
        'fine': 12.0,      # tonnes/ha
        'medium': 8.0,
        'coarse': 20.0
    },
    'surface_area_volume': 6500,  # m²/m³
    'fuel_depth': 1.8,    # meters
    'moisture_extinction': 25,  # %

    # Empirical ROS equation (not FBP)
    'ros_base': 15.0,     # m/min at 10 km/h wind
    'wind_factor': 0.35,  # ROS increases 35% per 10 km/h
    'slope_factor': 0.12,

    # Fire intensity
    'heat_content': 19500,  # kJ/kg
    'reaction_intensity': 'high',

    # Special conditions
    'santa_ana_multiplier': 1.5  # Santa Ana conditions
}
```

### Step 3: Calibration Against Historical Fires

Use validation cases to tune parameters:
1. **Palisades 2025:** 6,879 ha (24h), Wind=130 km/h
2. **Camp Fire 2018:** 62,053 ha (17 days), Wind=80 km/h
3. **Thomas Fire 2017:** 114,078 ha (40 days), Wind=100 km/h
4. **Tubbs Fire 2017:** 14,972 ha (3 days), Wind=110 km/h

Target: <30% error across all four fires

### Step 4: Integration

Add to FBP calculator:

```python
def get_fire_behavior(fuel_type, wind_speed, ffmc, ...):
    if fuel_type == 'CH1':
        # Use chaparral-specific equations
        return calculate_chaparral_behavior(wind_speed, ffmc, ...)
    else:
        # Use standard FBP equations
        return calculate_fbp_behavior(fuel_type, ...)
```

## Expected Impact

- Palisades Fire: 109% error → <30% error
- Enable California fire predictions
- Demonstrate model extensibility to non-Canadian ecosystems

## Validation

After implementation, re-run:
```bash
python3 tools/run_palisades_scenario.py
```

Target: Within 30% of 6,879 ha actual

## References

- Rothermel, R.C., 1972. A mathematical model for predicting fire spread in wildland fuels
- Anderson, H.E., 1982. Aids to determining fuel models for estimating fire behavior
- Cohen, J.D., 1986. Estimating fire behavior with FIRECAST: User's manual
- California Fire Lab studies on chaparral fire behavior
- Scott, J.H., 2005. Standard Fire Behavior Fuel Models

## DNA Update

```json
{
  "patterns_known": ["california_chaparral_fire_behavior", "chaparral_fuel_loading"],
  "fuel_types_mastered": ["CH1_california_chaparral"],
  "ecosystems_supported": ["canadian_boreal", "canadian_mountain", "california_chaparral"]
}
```
