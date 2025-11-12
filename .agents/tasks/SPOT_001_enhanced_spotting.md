# Task: SPOT_001 - Enhanced Spotting for Crown Fires

**Priority:** P1 (High)
**Assigned To:** fire-behavior-specialist-agent
**Status:** READY
**Created:** 2025-10-28
**Effort:** Low (2-3 hours)

## Problem

Current spotting probability (5%) too low for active crown fires. Fort McMurray showed extensive spotting creating secondary ignitions.

## Scientific Basis

Active crown fires (CFB >0.9) produce abundant firebrands:
- Firebrand generation rate: 10^5 - 10^6 brands per hectare
- Spotting distance: up to 10 km documented
- Secondary ignition probability increases exponentially with fire intensity

## Solution

Scale spotting based on crown fire involvement:

```python
def calculate_spotting_probability(cfb, fire_intensity_kwm, iteration):
    """
    Calculate spotting probability for current timestep

    Args:
        cfb: Crown fraction burned (0-1)
        fire_intensity_kwm: Fire line intensity (kW/m)
        iteration: Current iteration number

    Returns:
        Probability of spot fire this iteration
    """
    base_prob = 0.05

    if cfb > 0.9:  # Active crown fire
        # High intensity crown fires spot frequently
        crown_fire_multiplier = 3.0

        # Very intense fires spot even more
        if fire_intensity_kwm > 50000:
            intensity_multiplier = 1.5
        else:
            intensity_multiplier = 1.0

        spotting_prob = base_prob * crown_fire_multiplier * intensity_multiplier

    elif cfb > 0.5:  # Passive crown fire
        spotting_prob = base_prob * 1.5

    else:  # Surface fire
        spotting_prob = base_prob

    # Cap at reasonable maximum
    return min(spotting_prob, 0.25)
```

## Integration

Update spotting model in `fire_model_agent.py`:

```python
# Calculate dynamic spotting probability
spot_prob = calculate_spotting_probability(
    cfb=fbp_result['cfb'],
    fire_intensity_kwm=fbp_result['fi'],
    iteration=iteration
)

# Use in cellular automaton
if SPOTTING_ENABLED and np.random.random() < spot_prob:
    # Generate spot fire
    ...
```

## Expected Impact

- Increase long-range fire propagation
- Better match Fort McMurray's rapid spread pattern
- More realistic fire perimeter fragmentation

## Validation

Fort McMurray 2016: Should see increased area closer to 85,000 ha

## References

- Koo, E., et al., 2010. Firebrands and spotting ignition in large-scale fires. International Journal of Wildland Fire, 19(7), pp.818-843.
- Albini, F.A., 1979. Spot fire distance from burning trees-a predictive model. USDA Forest Service General Technical Report INT-GTR-56.

## DNA Update

```json
{
  "patterns_known": ["crown_fire_spotting_frequency", "cfb_driven_spotting"],
  "scientific_references": ["Koo 2010", "Albini 1979"]
}
```
