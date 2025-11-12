# Fluid Dynamics & Climate Change in Fire Modeling
## Professor's Teaching Module for the Team

**Date**: 2025-10-29
**Prepared by**: Professor Agent
**For**: Fire Model Development Team

---

## 📚 Learning Objectives

By the end of this tutorial, you will understand:

1. How fluid dynamics principles apply to wildfire behavior
2. Impact of climate change on fuel moisture and fire intensity
3. How to integrate these concepts into our fire model
4. Implementation priorities and code changes needed

---

## Part 1: Fluid Dynamics in Fire Modeling

### 1.1 Why Fluid Dynamics Matters

Wildfire is fundamentally a fluid dynamics problem:
- Fire generates heat → air rises (buoyancy)
- Rising air entrains oxygen → sustains combustion
- Wind + buoyancy create turbulence → enhances mixing
- Fire creates its own weather (pyrocumulonimbus)

### 1.2 Key Concepts

#### 1. Buoyancy-Driven Flow

**What it is**: Fire generates heat causing air to rise, creating convective flow patterns

**Math**: `Boussinesq approximation: ρ = ρ₀(1 - β(T - T₀))`

**Why it matters**: Critical for modeling plume rise and fire behavior on slopes

**How to implement**: Add buoyancy term to spread calculations based on temperature gradient

#### 2. Turbulent Mixing

**What it is**: Fire-induced turbulence enhances oxygen mixing and combustion

**Math**: `k-ε turbulence model or Large Eddy Simulation (LES)`

**Why it matters**: Affects fire intensity and rate of spread

**How to implement**: Incorporate turbulence factor based on fire intensity and wind speed

#### 3. Fire Whirls

**What it is**: Vorticity generation from buoyancy and wind shear creates rotating fire columns

**Math**: `Vorticity: ω = ∇ × v`

**Why it matters**: Can cause extreme fire behavior and long-range spotting

**How to implement**: Add vorticity threshold for fire whirl formation under high wind + intense fire

#### 4. Entrainment

**What it is**: Fire plume entrains ambient air, diluting smoke and affecting combustion

**Math**: `Entrainment velocity: vₑ = α × w (α ≈ 0.1)`

**Why it matters**: Affects plume height and oxygen availability

**How to implement**: Model oxygen depletion in high-intensity fires

#### 5. Radiation Heat Transfer

**What it is**: Fire emits thermal radiation affecting unburned fuel ahead of fire front

**Math**: `Stefan-Boltzmann: q = εσT⁴`

**Why it matters**: Pre-heats fuel, accelerating fire spread

**How to implement**: Add radiation factor to ROSf based on fire intensity


---

## Part 2: Climate Change Impacts

### 2.1 Why Climate Change Matters for Fire

Climate change affects fire through:
- Longer fire seasons (earlier snowmelt, later first snow)
- Higher temperatures → faster fuel drying
- Altered precipitation patterns → deeper droughts
- More extreme fire weather days

### 2.2 Buildup Index (BUI) Under Climate Change

BUI = f(DMC, DC) measures deep fuel moisture.

**Historical trend**: BUI increased ~15% since 1980s in Canadian boreal forest

**Projection**: BUI values > 80 days expected to increase 50-100% by 2050

**Impact**: Higher BUI = deeper burning, more intense fires, longer duration

### 2.3 Precipitation Changes

#### 1. Buildup Index (BUI) Trends

BUI = f(DMC, DC) increases with longer dry periods under climate change

**Relevance**: Higher BUI = deeper burning, higher intensity, more difficult suppression

**Implementation**: Add climate adjustment factor: BUI_adjusted = BUI × (1 + 0.002 × years_since_2020)

#### 2. Precipitation Intensity vs Duration

Climate change shifts precipitation: fewer events, higher intensity

**Relevance**: Drought Code accumulation accelerates despite unchanged total precipitation

**Implementation**: Weight DC reduction by precipitation duration, not just amount

#### 3. Fuel Moisture Lag

Heavy fuels (DC, DMC) respond slowly to precipitation

**Relevance**: Single rain event may reduce FFMC but not DC

**Implementation**: Exponential decay: DC_new = DC_old × exp(-P/τ), τ = 52 days

#### 4. Temperature-Precipitation Coupling

Warmer temperatures increase evapotranspiration, drying fuels faster

**Relevance**: Fire season lengthens and intensifies

**Implementation**: Temperature correction: DC_change += α × (T - T_ref), α = 2.0

#### 5. Compound Extremes

Hot-dry-windy days cluster more frequently under climate change

**Relevance**: More days with extreme fire potential

**Implementation**: Track multi-day heat waves and adjust fire risk accordingly


---

## Part 3: Integration into Our Model

### 3.1 Current Model Capabilities

Our model already has:
- ✅ FBP system (spread, intensity)
- ✅ Crown fire module
- ✅ Spotting model (Albini)
- ✅ Weather inputs (FFMC, DMC, DC, wind)

### 3.2 What We Need to Add

Priority additions:
1. Climate adjustment to BUI
2. Buoyancy factor for slope effects
3. Precipitation duration weighting
4. Fire whirl detection (advanced)

### 3.3 Where to Make Changes

**File**: `src/fire/fbp.py`
- BUI calculation (add climate factor)
- DC update (weight by precipitation duration)
- Temperature correction

**File**: `src/fire/fire_model.py`
- Spread calculation (add buoyancy factor)
- Intensity calculation (add turbulence)

**File**: `src/fire/spotting_model.py`
- Add fire whirl detection module

---

## Part 4: Implementation Roadmap

### Phase 1: Quick Wins (1 week)

**Features**: Climate-Adjusted BUI, Buoyancy Factor

**Deliverable**: Updated FBP with climate and buoyancy factors

**Validation**: Test on historical fires with known climate trends

### Phase 2: Precipitation Dynamics (2 weeks)

**Features**: Precipitation Duration Weighting, Temperature-DC coupling

**Deliverable**: Improved fuel moisture dynamics

**Validation**: Compare DC evolution with weather station data

### Phase 3: Advanced Fluid Dynamics (1 month)

**Features**: Fire Whirl Detection, Turbulent Mixing

**Deliverable**: Enhanced fire behavior under extreme conditions

**Validation**: Test on extreme fire case studies


---

## 📖 Recommended Reading


- **Large Eddy Simulation of wildfire spread**
  Linn et al. (2002)
  *International Journal of Wildland Fire*
  Key finding: LES captures fire-atmosphere interactions better than RANS

- **Physics-based modeling of wildfire-atmosphere interactions**
  Coen et al. (2013)
  *Atmospheric Chemistry and Physics*
  Key finding: Coupled fire-atmosphere models predict fire behavior more accurately

- **Vorticity-driven lateral spread of wildfires**
  Finney et al. (2015)
  *Combustion and Flame*
  Key finding: Fire-induced vorticity can cause lateral fire spread

- **Increasing fire weather in Canada under climate change**
  Flannigan et al. (2016)
  *Climate Change*
  Key finding: Fire season length increased 20% since 1970s in Canada

- **Drought code projections for North America**
  Wang et al. (2015)
  *Forest Ecology and Management*
  Key finding: DC > 400 days projected to increase 50-100% by 2100

- **Precipitation intensity and fuel moisture dynamics**
  Ruffault & Martin-StPaul (2020)
  *Environmental Research Letters*
  Key finding: Precipitation distribution matters more than total amount


---

## 🎯 Next Steps for Team

1. **Read this tutorial** - Understand concepts and rationale
2. **Review implementation guide** - See specific code changes
3. **Start with Phase 1** - Quick wins (climate BUI + buoyancy)
4. **Validate results** - Test on historical fires
5. **Iterate** - Move to Phase 2 and 3

---

## ❓ Questions for Discussion

1. Do we have historical precipitation intensity data for validation?
2. What climate change scenario should we use (RCP 4.5 or 8.5)?
3. Should we make climate adjustment user-configurable?
4. How do we validate buoyancy factor parameter (β)?

---

**Prepared by Professor Agent** | Literature Research Module
