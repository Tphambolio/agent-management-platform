# Implementation Guide - Code Changes
## Fluid Dynamics & Climate Integration

**For**: Development Team
**Priority**: Start with HIGH priority items

---

## Quick Wins (Phase 1)

### 1. Climate-Adjusted BUI

**File**: `src/fire/fbp.py`

**Current code** (around line 150):
```python
def calculate_bui(dmc, dc):
    '''Calculate Buildup Index from DMC and DC'''
    if dmc <= 0.4 * dc:
        bui = (0.8 * dc * dmc) / (dmc + 0.4 * dc)
    else:
        bui = dmc - (1 - 0.8 * dc / (dmc + 0.4 * dc)) * (0.92 + (0.0114 * dmc)**1.7)

    return max(0, bui)
```

**Add climate adjustment**:
```python
def calculate_bui(dmc, dc, year=2024, baseline_year=2020):
    '''Calculate Buildup Index with climate change adjustment'''
    # Standard BUI calculation
    if dmc <= 0.4 * dc:
        bui = (0.8 * dc * dmc) / (dmc + 0.4 * dc)
    else:
        bui = dmc - (1 - 0.8 * dc / (dmc + 0.4 * dc)) * (0.92 + (0.0114 * dmc)**1.7)

    # Climate change adjustment (Flannigan et al. 2016)
    years_since_baseline = max(0, year - baseline_year)
    climate_factor = 0.002  # 0.2% increase per year
    climate_adjustment = 1.0 + (climate_factor * years_since_baseline)

    bui_adjusted = bui * climate_adjustment

    return max(0, bui_adjusted)
```

**Validation**:
- Test with historical BUI data from 2000-2024
- Verify trend matches observed +15% increase

---

### 2. Buoyancy Factor in Spread

**File**: `src/fire/fire_model.py`

**Current spread calculation** (around line 450):
```python
# Apply slope factor
ros = ros_base * slope_factor

# Apply wind factor
ros = ros * wind_factor
```

**Add buoyancy factor**:
```python
# Apply slope factor
ros = ros_base * slope_factor

# Apply buoyancy factor (for upslope fire on steep terrain)
if slope_pct > 20 and fire_intensity > 5000:  # kW/m
    # Buoyancy enhances upslope spread
    buoyancy_factor = 1.0 + 0.15 * (slope_pct / 100.0) * (fire_intensity / 10000.0)
    buoyancy_factor = min(buoyancy_factor, 1.5)  # Cap at 50% increase
    ros = ros * buoyancy_factor

# Apply wind factor
ros = ros * wind_factor
```

**Parameters**:
- β = 0.15 (calibration parameter, needs validation)
- Threshold: slope > 20%, intensity > 5000 kW/m
- Max factor: 1.5x

**Validation**:
- Test on slope fires (e.g., 2020 Creek Fire, CA)
- Compare to observed upslope run rates

---

## Medium Priority (Phase 2)

### 3. Precipitation Duration Weighting

**File**: `src/fire/fbp.py`

**Current DC update** (simplified):
```python
def update_dc(dc_yesterday, temp, precip):
    '''Update Drought Code'''
    # Precipitation effect
    if precip > 2.8:
        dc_after_rain = dc_yesterday - 400.0 * log(1 + (precip * 3.937) / 800)
    else:
        dc_after_rain = dc_yesterday

    # Drying effect
    dc_today = dc_after_rain + drying_factor(temp)

    return max(0, dc_today)
```

**Add duration weighting**:
```python
def update_dc(dc_yesterday, temp, precip, precip_duration_hours=24):
    '''Update Drought Code with precipitation duration weighting'''
    # Precipitation effect - weighted by duration
    if precip > 2.8:
        # Longer duration = more DC reduction (up to 24h)
        duration_factor = min(1.0, precip_duration_hours / 24.0)

        # Base reduction
        base_reduction = 400.0 * log(1 + (precip * 3.937) / 800)

        # Apply duration weighting
        dc_after_rain = dc_yesterday - (base_reduction * duration_factor)
    else:
        dc_after_rain = dc_yesterday

    # Drying effect (enhanced by temperature)
    drying = drying_factor(temp)

    # Temperature correction (warmer = faster drying)
    temp_correction = 2.0 * max(0, temp - 20.0)  # Extra drying above 20°C

    dc_today = dc_after_rain + drying + temp_correction

    return max(0, dc_today)
```

**Data needed**:
- Precipitation duration from weather stations (or estimate from intensity)

---

## Advanced (Phase 3)

### 4. Fire Whirl Detection

**New file**: `src/fire/fire_whirl.py`

```python
def detect_fire_whirl_risk(wind_speed, fire_intensity, terrain_roughness=500):
    '''
    Detect conditions favorable for fire whirl formation

    Args:
        wind_speed: Wind speed (km/h)
        fire_intensity: Fire intensity (kW/m)
        terrain_roughness: Terrain roughness parameter (default 500)

    Returns:
        whirl_risk: Risk score (0-10+)
        whirl_likely: Boolean if risk exceeds threshold
    '''
    # Fire whirl risk formula (simplified from Finney et al. 2015)
    # Risk increases with wind and fire intensity
    # Risk decreases with terrain roughness

    whirl_risk = (wind_speed * (fire_intensity / 1000.0)) / (1.0 + terrain_roughness / 1000.0)

    # Threshold for fire whirl formation
    whirl_likely = whirl_risk > 5.0

    # If fire whirl likely, enhance spotting distance
    if whirl_likely:
        spotting_multiplier = 1.0 + min(2.0, whirl_risk / 10.0)  # Up to 3x
    else:
        spotting_multiplier = 1.0

    return {
        'whirl_risk': whirl_risk,
        'whirl_likely': whirl_likely,
        'spotting_multiplier': spotting_multiplier
    }
```

**Integration in** `src/fire/spotting_model.py`:
```python
# Check for fire whirl conditions
from fire_whirl import detect_fire_whirl_risk

whirl_data = detect_fire_whirl_risk(wind_speed, fire_intensity)

if whirl_data['whirl_likely']:
    # Enhance spotting distance
    max_spot_distance *= whirl_data['spotting_multiplier']

    # Log fire whirl event
    print(f"⚠️  Fire whirl detected! Risk: {whirl_data['whirl_risk']:.1f}")
```

---

## Testing Strategy

### Unit Tests

```python
# test_climate_bui.py
def test_climate_adjustment():
    # 2020 baseline
    bui_2020 = calculate_bui(dmc=50, dc=300, year=2020)

    # 2050 with 30 years of climate change
    bui_2050 = calculate_bui(dmc=50, dc=300, year=2050)

    # Should be ~6% higher (0.2% × 30 years)
    expected_increase = 1.06
    assert abs(bui_2050 / bui_2020 - expected_increase) < 0.01
```

### Integration Tests

```python
# test_buoyancy.py
def test_upslope_buoyancy():
    # Steep slope + high intensity = buoyancy boost
    ros_flat = calculate_ros(slope=0, intensity=8000)
    ros_steep = calculate_ros(slope=40, intensity=8000)

    # Steep slope should be faster due to buoyancy
    assert ros_steep > ros_flat * 1.2  # At least 20% faster
```

---

## Validation Checklist

- [ ] Climate BUI matches historical trend (2000-2024)
- [ ] Buoyancy factor reasonable for slope fires
- [ ] Precipitation duration logic validated with weather data
- [ ] Fire whirl detection tested on extreme fire cases
- [ ] All changes documented in code comments
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Benchmark performance maintained (IoU > 0.75)

---

## Rollout Plan

1. **Week 1**: Implement climate BUI + buoyancy
2. **Week 2**: Test on historical fires, adjust parameters
3. **Week 3**: Implement precipitation duration weighting
4. **Week 4**: Validate against weather station data
5. **Week 5-6**: Fire whirl module (if time permits)
6. **Week 7**: Final validation and documentation

---

**Questions?** Review teaching materials or consult Professor Agent research notes.
