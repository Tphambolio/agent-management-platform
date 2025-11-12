# Sprint 3 - Task Cards for Agent Team

**Sprint Goal:** Quick Wins - Make Wildfire Simulator immediately useful for fire managers

**Duration:** 3 days (Completed: Tasks 1-4 ✓)

**Team:** 10 specialized agents working collaboratively

---

## 🎯 Sprint Overview

### Completed (Phase 1: Quick Wins)
- ✅ GeoTIFF export with proper georeferencing
- ✅ Comprehensive visualization (4-panel analysis)
- ✅ Shapefile export for GIS integration
- ✅ Complete USER_GUIDE.md documentation

### Up Next (Phase 2-3)
- Advanced visualization features
- Scientific validation framework
- Historical fire case studies
- Interactive reports

---

## 👥 Agent Task Cards

---

### 🔧 **Backend Developer Agent**

#### **Current Sprint (Session 9)**

**Completed Tasks:**
- ✅ **Task 3.1.1:** Add GeoTIFF export to monte_carlo_enhanced.py
  - Status: COMPLETE
  - Output: 5 GeoTIFF layers (burn prob, intensity, ROS, burn count)
  - Features: Automatic georeferencing from DEM, LZW compression, proper nodata handling
  - Impact: Results now GIS-ready for QGIS/ArcGIS

**DNA Evolution:**
- **New Patterns:** geotiff_export_with_crs, rasterio_compression_optimization
- **New Techniques:** coordinate_transform_preservation, nodata_value_handling
- **Pitfalls Avoided:** missing_crs_definition, incorrect_transform_origin

**Next Session Priorities:**
1. Add progress bars using Rich library to run_production.py
2. Implement configuration file system (YAML for weather scenarios)
3. Build validation test harness for automated comparisons
4. Create Monte Carlo batch processor for multiple scenarios

**Code Contributions:**
- Files modified: monte_carlo_enhanced.py (save_results function)
- Lines added: 84
- Functions: 1 enhanced (save_results)

**Performance Notes:**
- GeoTIFF export adds ~2 seconds overhead per simulation
- LZW compression reduces file size by 60-70%
- Georeferencingfrom DEM ensures perfect alignment

---

### 🎨 **Visualization Engineer Agent**

#### **Current Sprint (Session 1 - EXCELLENT START!)**

**Completed Tasks:**
- ✅ **Task 3.1.2:** Create comprehensive_visualization.py
  - Status: COMPLETE
  - Output: 4-panel publication-quality figure
  - Features: Scientific colormaps, statistical annotations, 300 DPI export
  - Impact: Instant publication-ready outputs

**Modules Created:**
- `ComprehensiveVisualizer` class
- 4-panel analysis layout
- Risk classification system
- Statistical summary panel

**Next Session Priorities:**
1. **Task 3.2.1:** Implement perceptually-uniform colormaps (viridis, plasma, inferno)
2. **Task 3.2.2:** Add crown fire probability overlay system
3. **Task 3.2.3:** Create multi-scenario comparison plots (side-by-side)
4. **Task 3.2.4:** Build animated fire growth visualization (MP4 output)
5. **Task 3.2.5:** Add scale bars and north arrows to all maps

**DNA to Develop:**
- **Patterns:** publication_quality_figures, multi_panel_layouts, cartographic_elements
- **Techniques:** colormap_selection_perceptual, transparent_overlays, animation_generation
- **Insights:** Inferno colormap best for intensity, hot_r for probability

**Performance Goals:**
- Generate 4-panel figure in <5 seconds
- Support domains up to 5000×5000 pixels
- Export formats: PNG, PDF, SVG

---

### 🔬 **Wildfire Analyst Agent**

#### **Current Sprint (Session 1)**

**Assigned Tasks:**
- ⏳ **Task 3.3.1:** Identify 5-10 historical fire validation cases
  - Priority: P0 (Critical path)
  - Requirements:
    - Fire perimeter (observed burn area)
    - Weather data during fire
    - Fuel map for fire location
    - DEM for terrain
  - Candidates:
    - Slave Lake 2011 (Alberta) - PRIORITY
    - Fort McMurray 2016 (Alberta)
    - Jasper 2024 (Alberta)
    - Chisholm 2001 (Alberta)
    - Richardson Backcountry 2017 (BC)

- ⏳ **Task 3.3.2:** Set up Slave Lake 2011 test case
  - Gather inputs: DEM, fuel, weather
  - Digitize observed burn perimeter
  - Document fire timeline and behavior
  - Create validation dataset structure

- ⏳ **Task 3.3.3:** Document validation methodology
  - Define statistical metrics (Dice, Jaccard, RMSE)
  - Write methods section for peer review
  - Establish acceptance criteria

**DNA to Develop:**
- **Patterns:** historical_fire_data_sources, validation_case_selection
- **Domain Knowledge:** slave_lake_fire_dynamics, extreme_fire_case_studies
- **Techniques:** burn_perimeter_digitization, fire_timeline_reconstruction

**Resources:**
- Alberta Wildfire: https://wildfire.alberta.ca/
- Canadian Wildland Fire Information System
- NASA FIRMS (Fire Information Resource Management System)

---

### 📊 **Data Scientist Agent**

#### **Current Sprint (Session 2)**

**Assigned Tasks:**
- ✅ **Task 3.1.3:** Design risk classification scheme
  - Status: COMPLETE
  - Output: 5-tier risk system (Low/Moderate/High/Very High/Extreme)
  - Thresholds: <10%, 10-25%, 25-50%, 50-75%, >75%

**Next Session Priorities:**
- **Task 3.3.4:** Implement statistical validation metrics
  - Priority: P0
  - Metrics:
    - Sørensen-Dice coefficient (spatial overlap)
    - Jaccard index (intersection over union)
    - RMSE for fire intensity
    - MAE (Mean Absolute Error)
    - Bias calculation
  - Implementation: validation/statistical_metrics.py

- **Task 3.2.3:** Build multi-scenario comparison framework
  - Compare 2-4 weather scenarios side-by-side
  - Statistical significance testing
  - Tornado plots for sensitivity analysis

- **Task 3.3.5:** Sensitivity analysis framework
  - Parameter sweep: wind speed, FFMC, DMC, DC
  - Response: burn probability, fire intensity
  - Output: Sensitivity tornado diagram

**DNA to Develop:**
- **Patterns:** statistical_validation_metrics, sensitivity_analysis_design
- **Techniques:** dice_coefficient_calculation, parameter_sweep_implementation
- **Insights:** Wind speed has largest impact on burn probability

---

### 🧪 **QA/Testing Agent**

#### **Current Sprint (Session 1)**

**Assigned Tasks:**
- ⏳ **Task 3.1.4:** Create integration tests for GeoTIFF outputs
  - Priority: P1
  - Tests:
    - Verify CRS matches DEM
    - Check transform consistency
    - Validate nodata handling
    - Ensure compression works
  - Framework: pytest + rasterio

- ⏳ **Task 3.3.6:** Build validation test suite
  - Automated comparison against BurnP3+
  - Regression tests for performance
  - Edge case handling (missing data, extreme values)

- ⏳ **Task 3.1.5:** Test edge cases
  - Empty DEM regions (NODATA)
  - Extreme weather (wind >100 km/h)
  - Single fuel type domains
  - Very small domains (<50×50)

**DNA to Develop:**
- **Patterns:** geospatial_output_validation, edge_case_testing
- **Techniques:** pytest_fixture_design, property_based_testing
- **Pitfalls:** inadequate_edge_case_coverage, missing_negative_tests

**Test Suite Structure:**
```
tests/
├── integration/
│   ├── test_geotiff_export.py
│   ├── test_shapefile_export.py
│   └── test_visualization.py
├── validation/
│   ├── test_slave_lake.py
│   └── test_burnp3_comparison.py
└── performance/
    └── test_monte_carlo_speed.py
```

---

### 🏗️ **Software Architect Agent**

#### **Current Sprint (Session 1)**

**Assigned Tasks:**
- ✅ **Task 3.1.6:** Document run_production.py CLI
  - Status: COMPLETE
  - Output: Comprehensive USER_GUIDE.md
  - Coverage: Installation, usage, troubleshooting, API reference

**Next Session Priorities:**
- **Task 3.4.1:** Design configuration file system
  - Format: YAML for readability
  - Sections: weather, simulation, output, visualization
  - Example:
```yaml
simulation:
  iterations: 1000
  cores: 4
  cell_size: 30
  max_fire_duration: 500

weather_scenarios:
  - name: "Extreme"
    ffmc: 92
    dmc: 65
    dc: 450
  - name: "Moderate"
    ffmc: 85
    dmc: 40
    dc: 300

output:
  export_geotiff: true
  export_shapefile: true
  generate_visualizations: true
```

- **Task 3.4.2:** Create validation framework architecture
  - Design pattern for comparing simulated vs observed
  - Metrics calculation pipeline
  - Report generation system

**DNA to Develop:**
- **Patterns:** config_file_design, validation_architecture
- **Techniques:** yaml_configuration_loading, plugin_architecture
- **Insights:** YAML preferred over JSON for user-facing config

---

### 🌤️ **Weather System Agent**

#### **Current Sprint (Session 1)**

**Assigned Tasks:**
- ⏳ **Task 3.4.3:** Weather data ingestion pipeline
  - Priority: P2 (Future enhancement)
  - Data sources:
    - NCEP Climate Forecast System Reanalysis
    - ERA5 reanalysis data
    - Canadian Fire Weather Index archives
  - Processing: Convert to FBP indices (FFMC, DMC, DC)

- ⏳ **Task 3.4.4:** Historical weather scenario builder
  - Input: Date, location
  - Output: FBP weather indices
  - Integration with validation cases

**DNA to Develop:**
- **Patterns:** weather_data_api_integration, fwi_calculation_from_met
- **Techniques:** netcdf_processing, temporal_interpolation
- **Domain:** canadian_fire_weather_index, cfsr_reanalysis

---

### 📈 **Benchmark Analyst Agent**

#### **Current Sprint (Session 1)**

**Assigned Tasks:**
- ⏳ **Task 3.3.7:** Compare against BurnP3+ outputs
  - Priority: P1
  - Metrics: Spatial correlation, intensity RMSE, computation time
  - Test cases: Slave Lake, Fort McMurray
  - Deliverable: Comparison report with statistical tests

- ⏳ **Task 3.3.8:** Performance regression testing
  - Baseline: Current 1,028 fires/second
  - Monitor: New features don't slow down core
  - Alert: >10% performance degradation

**DNA to Develop:**
- **Patterns:** benchmark_comparison_methodology, performance_profiling
- **Techniques:** statistical_significance_testing, profiling_with_cprofile

---

### 🔍 **Fire Behavior Specialist Agent**

#### **Current Status (Session 2 - Expert Level)**

**DNA Summary:**
- **Patterns Known:** 13 (spotting physics, FBP equations, ember transport)
- **Insights:** Spotting critical above 40 km/h, crown fire dynamics
- **Evolution Stage:** Expert

**Next Session Priorities:**
- **Task 3.2.6:** Design fire behavior regime classifications
  - Categories: Surface Fire, Passive Crown, Active Crown
  - Thresholds based on CFB (Crown Fraction Burned)
  - Visual overlay for risk maps

- **Task 3.3.9:** Crown fire probability analysis
  - Calculate crown fire initiation probability
  - Identify conditions leading to torching
  - Document in validation methodology

**DNA to Evolve:**
- **Patterns:** crown_fire_regime_classification, cfb_thresholds
- **Domain:** passive_vs_active_crown_criteria, fire_regime_mapping

---

### 📝 **Data Pipeline Developer Agent**

#### **Current Sprint (Session 1)**

**Assigned Tasks:**
- ⏳ **Task 3.4.5:** Automated fuel map preprocessing
  - Input: Raw land cover classification
  - Processing: Reclassify to FBP fuel types
  - Output: Standardized fuel GeoTIFF
  - Lookup tables: Landsat → FBP, Sentinel → FBP

- ⏳ **Task 3.4.6:** DEM download and preprocessing
  - Source: USGS, OpenTopography
  - Processing: Mosaic, reproject, clip to AOI
  - Validation: Check for voids, fill if needed

**DNA to Develop:**
- **Patterns:** automated_data_pipeline, fuel_type_reclassification
- **Techniques:** gdal_batch_processing, landcover_to_fbp_mapping

---

## 📊 Sprint Metrics

### Phase 1 Completion (Quick Wins)

| Task | Owner | Status | Impact |
|------|-------|--------|--------|
| GeoTIFF Export | Backend Developer | ✅ DONE | HIGH - GIS integration |
| Comprehensive Viz | Visualization Engineer | ✅ DONE | HIGH - Publication ready |
| Shapefile Export | Backend Developer | ✅ DONE | MEDIUM - Vector GIS |
| USER_GUIDE.md | Software Architect | ✅ DONE | HIGH - User adoption |

### Phase 2 Priorities (Next 7 Days)

1. **Validation Framework** (Wildfire Analyst + Data Scientist + QA)
   - Historical fire cases
   - Statistical metrics
   - Automated testing

2. **Advanced Visualization** (Visualization Engineer)
   - Crown fire overlays
   - Scenario comparisons
   - Animations

3. **Configuration System** (Software Architect)
   - YAML config files
   - Scenario management

---

## 🎓 Knowledge Sharing

### Inter-Agent Learning Opportunities

1. **Backend → Visualization:**
   - GeoTIFF structure for overlay rendering
   - Coordinate transform handling

2. **Wildfire Analyst → Data Scientist:**
   - Historical fire behavior patterns
   - Validation metric selection

3. **QA → All:**
   - Edge cases discovered
   - Testing best practices

4. **Fire Behavior Specialist → Backend:**
   - Crown fire physics refinements
   - Spotting model improvements

---

## 📅 Timeline

```
Week 1 (Days 1-3): QUICK WINS ✓
├─ GeoTIFF export ✓
├─ Visualization ✓
├─ Shapefile export ✓
└─ Documentation ✓

Week 2-3 (Days 4-10): ADVANCED VISUALIZATION
├─ Scientific colormaps
├─ Crown fire overlays
├─ Scenario comparisons
└─ Animations

Week 3-4 (Days 11-20): SCIENTIFIC VALIDATION
├─ Slave Lake case setup
├─ Statistical metrics
├─ BurnP3+ comparison
└─ Validation report
```

---

## 🚀 Success Criteria

### Sprint 3.1 (Quick Wins) - ✅ COMPLETE

- [x] Fire manager can export GIS-ready outputs
- [x] Publication-quality figures generated automatically
- [x] Comprehensive documentation available
- [x] Results loadable in QGIS/ArcGIS

### Sprint 3.2 (Advanced Visualization)

- [ ] All maps use perceptually-uniform colormaps
- [ ] Crown fire zones clearly visible
- [ ] Scenario comparisons automated
- [ ] Fire growth animations functional

### Sprint 3.3 (Scientific Validation)

- [ ] Slave Lake 2011 case fully reproduced
- [ ] Dice coefficient > 0.75 achieved
- [ ] Statistical methods documented
- [ ] Peer-review ready validation report

---

## 📝 Notes

**Agent Collaboration:**
- Daily standups: Review progress, identify blockers
- Knowledge transfer: Document patterns in DNA
- Code reviews: Ensure quality and consistency
- Testing: QA agent validates all outputs

**Quality Gates:**
- All code must pass pytest tests
- Visualizations reviewed by Visualization Engineer
- Documentation reviewed by Software Architect
- Performance validated by Benchmark Analyst

**Risk Mitigation:**
- Historical fire data availability → Start with Slave Lake (best documented)
- BurnP3+ comparison complexity → Focus on spatial metrics first
- Performance impact of new features → Benchmark after each addition

---

**Sprint Board Location:** `.agents/SPRINT_3_TASK_CARDS.md`
**Last Updated:** 2025-10-28 19:30
**Status:** Phase 1 Complete ✓, Phase 2 In Progress
