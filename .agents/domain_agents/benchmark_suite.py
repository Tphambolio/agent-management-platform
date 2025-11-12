#!/usr/bin/env python3
"""Performance Benchmark Suite - Performance Tuning Agent
Complete benchmarking framework for wildfire simulator
"""

import numpy as np
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.fbp_calculator_fast import fbp_calculate, fbp_calculate_array
from src.core.fbp_calculator import get_fire_behavior as get_fire_behavior_slow
from src.simulation.monte_carlo_enhanced import EnhancedMonteCarloSimulator
from src.core.fire_spread import FireSpreadSimulator

def benchmark_fbp():
    print('='*70)
    print('FBP CALCULATOR BENCHMARK')
    print('='*70)
    
    n = 10000
    print(f'\nNumba JIT version ({n:,} iterations):')
    start = time.time()
    for _ in range(n):
        fbp_calculate(1, 30.0, 92.0, 60.0, 400.0, 10.0, 50.0)
    elapsed = time.time() - start
    print(f'  Throughput: {n/elapsed:,.0f} calcs/sec')
    
    print(f'\nVectorized version (100,000 cells):')
    n_cells = 100000
    fuel_idx = np.ones(n_cells, dtype=np.int32)
    wind = np.random.uniform(10, 40, n_cells)
    ffmc = np.random.uniform(85, 95, n_cells)
    dmc = np.random.uniform(30, 70, n_cells)
    dc = np.random.uniform(200, 500, n_cells)
    slope = np.random.uniform(0, 20, n_cells)
    
    start = time.time()
    results = fbp_calculate_array(fuel_idx, wind, ffmc, dmc, dc, slope)
    elapsed = time.time() - start
    print(f'  Throughput: {n_cells/elapsed:,.0f} cells/sec')

def benchmark_monte_carlo():
    print('\n' + '='*70)
    print('MONTE CARLO PARALLELIZATION BENCHMARK')
    print('='*70)
    
    fuel = np.ones((50, 50), dtype=int) * 2
    elev = np.random.rand(50, 50) * 20 + 500
    weather = [{'ffmc': 85, 'dmc': 40, 'dc': 300}]
    
    for n_cores in [1, 2, 4]:
        print(f'\n{n_cores} cores (20 iterations):')
        mc = EnhancedMonteCarloSimulator(fuel, elev, weather, n_iterations=20)
        start = time.time()
        result = mc.run(n_cores=n_cores, random_ignitions=True)
        elapsed = time.time() - start
        print(f'  Throughput: {20/elapsed:.2f} fires/sec')

if __name__ == '__main__':
    print('\nPERFORMANCE TUNING AGENT - BENCHMARK SUITE')
    benchmark_fbp()
    benchmark_monte_carlo()
    print('\n' + '='*70)
    print('✓ BENCHMARK COMPLETE')
    print('='*70)
