#!/usr/bin/env node
/**
 * Agent Management Platform - Deployment Integration Tests
 *
 * This script tests the entire deployment stack:
 * - Backend API (Railway)
 * - Frontend (Vercel)
 * - Integration between frontend and backend
 * - CORS configuration
 *
 * Usage: node test-deployment.js
 */

const https = require('https');
const http = require('http');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'https://crisiskitai-production.up.railway.app';
const FRONTEND_URL = process.env.FRONTEND_URL || 'https://frontend-jo4dadk2b-travis-kennedys-projects.vercel.app';

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

const results = {
  passed: 0,
  failed: 0,
  warnings: 0,
  tests: []
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logTest(name, status, details = '') {
  const icon = status === 'PASS' ? '✓' : status === 'FAIL' ? '✗' : '⚠';
  const color = status === 'PASS' ? 'green' : status === 'FAIL' ? 'red' : 'yellow';

  log(`${icon} ${name}`, color);
  if (details) {
    log(`  ${details}`, 'cyan');
  }

  results.tests.push({ name, status, details });
  if (status === 'PASS') results.passed++;
  else if (status === 'FAIL') results.failed++;
  else results.warnings++;
}

function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const protocol = urlObj.protocol === 'https:' ? https : http;

    const req = protocol.request(url, {
      method: options.method || 'GET',
      headers: options.headers || {},
      timeout: 10000,
      ...options
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data
        });
      });
    });

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    if (options.body) {
      req.write(options.body);
    }

    req.end();
  });
}

async function testBackendHealth() {
  log('\n=== Testing Backend (Railway) ===\n', 'bright');

  try {
    const res = await makeRequest(`${BACKEND_URL}/health`);

    if (res.statusCode === 200) {
      try {
        const data = JSON.parse(res.body);
        logTest('Backend Health Endpoint', 'PASS',
          `Status: ${data.status}, Agents: ${data.agents_discovered || 0}`);
        return data;
      } catch (e) {
        logTest('Backend Health Endpoint', 'FAIL',
          `Status 200 but invalid JSON: ${res.body.substring(0, 100)}`);
        return null;
      }
    } else if (res.statusCode === 502) {
      logTest('Backend Health Endpoint', 'FAIL',
        'Backend returning 502 Bad Gateway - container crashed or not responding');
      return null;
    } else if (res.statusCode === 503) {
      logTest('Backend Health Endpoint', 'FAIL',
        'Backend returning 503 Service Unavailable - still starting up?');
      return null;
    } else {
      logTest('Backend Health Endpoint', 'FAIL',
        `Unexpected status code: ${res.statusCode}`);
      return null;
    }
  } catch (error) {
    logTest('Backend Health Endpoint', 'FAIL',
      `Error: ${error.message}`);
    return null;
  }
}

async function testBackendRoot() {
  try {
    const res = await makeRequest(`${BACKEND_URL}/`);

    if (res.statusCode === 200) {
      try {
        const data = JSON.parse(res.body);
        logTest('Backend Root Endpoint', 'PASS',
          `Service: ${data.service}, Version: ${data.version}`);
        return data;
      } catch (e) {
        logTest('Backend Root Endpoint', 'WARN',
          'Status 200 but response is not JSON');
        return null;
      }
    } else {
      logTest('Backend Root Endpoint', 'FAIL',
        `Status code: ${res.statusCode}`);
      return null;
    }
  } catch (error) {
    logTest('Backend Root Endpoint', 'FAIL',
      `Error: ${error.message}`);
    return null;
  }
}

async function testBackendAPI() {
  try {
    const res = await makeRequest(`${BACKEND_URL}/api/agents`);

    if (res.statusCode === 200) {
      try {
        const data = JSON.parse(res.body);
        logTest('Backend API - Agents Endpoint', 'PASS',
          `Found ${Array.isArray(data) ? data.length : 'unknown'} agents`);
        return data;
      } catch (e) {
        logTest('Backend API - Agents Endpoint', 'WARN',
          'Status 200 but invalid JSON');
        return null;
      }
    } else {
      logTest('Backend API - Agents Endpoint', 'FAIL',
        `Status code: ${res.statusCode}`);
      return null;
    }
  } catch (error) {
    logTest('Backend API - Agents Endpoint', 'FAIL',
      `Error: ${error.message}`);
    return null;
  }
}

async function testBackendCORS() {
  try {
    const res = await makeRequest(`${BACKEND_URL}/health`, {
      headers: {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'GET',
      }
    });

    const corsHeader = res.headers['access-control-allow-origin'];

    if (corsHeader) {
      if (corsHeader === FRONTEND_URL || corsHeader === '*') {
        logTest('Backend CORS Configuration', 'PASS',
          `Allows origin: ${corsHeader}`);
      } else {
        logTest('Backend CORS Configuration', 'WARN',
          `Allows: ${corsHeader}, but frontend is: ${FRONTEND_URL}`);
      }
    } else {
      logTest('Backend CORS Configuration', 'FAIL',
        'No Access-Control-Allow-Origin header found');
    }
  } catch (error) {
    logTest('Backend CORS Configuration', 'FAIL',
      `Error: ${error.message}`);
  }
}

async function testBackendDocs() {
  try {
    const res = await makeRequest(`${BACKEND_URL}/docs`);

    if (res.statusCode === 200) {
      logTest('Backend API Documentation', 'PASS',
        'API docs accessible at /docs');
    } else {
      logTest('Backend API Documentation', 'WARN',
        `Status code: ${res.statusCode}`);
    }
  } catch (error) {
    logTest('Backend API Documentation', 'FAIL',
      `Error: ${error.message}`);
  }
}

async function testFrontend() {
  log('\n=== Testing Frontend (Vercel) ===\n', 'bright');

  try {
    const res = await makeRequest(FRONTEND_URL);

    if (res.statusCode === 200) {
      const bodyLower = res.body.toLowerCase();

      // Check if it's an HTML page
      if (bodyLower.includes('<!doctype html') || bodyLower.includes('<html')) {
        logTest('Frontend Loading', 'PASS',
          'HTML page returned successfully');

        // Check for React root
        if (bodyLower.includes('id="root"')) {
          logTest('Frontend React App', 'PASS',
            'React root element found');
        } else {
          logTest('Frontend React App', 'WARN',
            'HTML returned but no React root element found');
        }

        // Check for script tags
        if (bodyLower.includes('<script')) {
          logTest('Frontend JavaScript', 'PASS',
            'JavaScript files referenced');
        } else {
          logTest('Frontend JavaScript', 'WARN',
            'No JavaScript files found');
        }
      } else {
        logTest('Frontend Loading', 'FAIL',
          'Status 200 but not HTML content');
      }
    } else if (res.statusCode === 404) {
      logTest('Frontend Loading', 'FAIL',
        '404 Not Found - Vercel build may have failed or wrong deployment');
    } else {
      logTest('Frontend Loading', 'FAIL',
        `Unexpected status code: ${res.statusCode}`);
    }
  } catch (error) {
    logTest('Frontend Loading', 'FAIL',
      `Error: ${error.message}`);
  }
}

async function testFrontendStaticAssets() {
  try {
    const res = await makeRequest(`${FRONTEND_URL}/assets`);

    // We expect either a 404 (no index) or 403 (forbidden directory listing)
    // Both are acceptable for static assets directory
    if (res.statusCode === 404 || res.statusCode === 403) {
      logTest('Frontend Static Assets', 'PASS',
        'Assets directory exists (security configured correctly)');
    } else if (res.statusCode === 200) {
      logTest('Frontend Static Assets', 'WARN',
        'Assets directory publicly listable (potential security issue)');
    }
  } catch (error) {
    logTest('Frontend Static Assets', 'WARN',
      'Could not check static assets');
  }
}

async function testIntegration() {
  log('\n=== Testing Frontend-Backend Integration ===\n', 'bright');

  // Test if frontend would be able to reach backend
  try {
    const res = await makeRequest(`${BACKEND_URL}/api/agents`, {
      headers: {
        'Origin': FRONTEND_URL,
        'Accept': 'application/json',
      }
    });

    const corsHeader = res.headers['access-control-allow-origin'];

    if (res.statusCode === 200 && corsHeader) {
      logTest('Frontend-Backend Communication', 'PASS',
        'Backend accessible from frontend origin');
    } else if (res.statusCode === 200 && !corsHeader) {
      logTest('Frontend-Backend Communication', 'FAIL',
        'Backend accessible but CORS not configured');
    } else {
      logTest('Frontend-Backend Communication', 'FAIL',
        `Backend returned status: ${res.statusCode}`);
    }
  } catch (error) {
    logTest('Frontend-Backend Communication', 'FAIL',
      `Error: ${error.message}`);
  }
}

function printSummary() {
  log('\n' + '='.repeat(50), 'bright');
  log('TEST SUMMARY', 'bright');
  log('='.repeat(50) + '\n', 'bright');

  log(`Total Tests: ${results.tests.length}`, 'cyan');
  log(`✓ Passed: ${results.passed}`, 'green');
  log(`✗ Failed: ${results.failed}`, 'red');
  log(`⚠ Warnings: ${results.warnings}`, 'yellow');

  if (results.failed > 0) {
    log('\n' + '='.repeat(50), 'bright');
    log('FAILED TESTS:', 'red');
    log('='.repeat(50) + '\n', 'bright');

    results.tests
      .filter(t => t.status === 'FAIL')
      .forEach(t => {
        log(`✗ ${t.name}`, 'red');
        log(`  ${t.details}`, 'cyan');
      });
  }

  log('\n' + '='.repeat(50), 'bright');
  log('RECOMMENDED ACTIONS:', 'yellow');
  log('='.repeat(50) + '\n', 'bright');

  const failedTests = results.tests.filter(t => t.status === 'FAIL');

  if (failedTests.some(t => t.name.includes('Backend'))) {
    log('Backend Issues Detected:', 'yellow');
    log('1. Check Railway deployment logs for errors', 'cyan');
    log('2. Verify CORS_ORIGINS environment variable is set', 'cyan');
    log('3. Ensure Dockerfile builds successfully', 'cyan');
    log('4. Check if container is crashing on startup\n', 'cyan');
  }

  if (failedTests.some(t => t.name.includes('Frontend'))) {
    log('Frontend Issues Detected:', 'yellow');
    log('1. Check Vercel deployment logs', 'cyan');
    log('2. Verify build completed successfully', 'cyan');
    log('3. Check VITE_API_URL environment variable', 'cyan');
    log('4. Ensure dist/ folder was generated\n', 'cyan');
  }

  if (failedTests.some(t => t.name.includes('CORS'))) {
    log('CORS Issues Detected:', 'yellow');
    log('1. Add CORS_ORIGINS to Railway environment variables', 'cyan');
    log('2. Set value to: ' + FRONTEND_URL, 'cyan');
    log('3. Redeploy backend after adding variable\n', 'cyan');
  }

  log('\nDeployment URLs:', 'bright');
  log(`Backend:  ${BACKEND_URL}`, 'cyan');
  log(`Frontend: ${FRONTEND_URL}`, 'cyan');
  log(`API Docs: ${BACKEND_URL}/docs\n`, 'cyan');
}

async function runTests() {
  log('\n' + '='.repeat(50), 'bright');
  log('AGENT MANAGEMENT PLATFORM - DEPLOYMENT TESTS', 'bright');
  log('='.repeat(50), 'bright');

  log('\nConfiguration:', 'cyan');
  log(`Backend URL:  ${BACKEND_URL}`, 'cyan');
  log(`Frontend URL: ${FRONTEND_URL}`, 'cyan');

  // Run all tests
  await testBackendHealth();
  await testBackendRoot();
  await testBackendAPI();
  await testBackendCORS();
  await testBackendDocs();

  await testFrontend();
  await testFrontendStaticAssets();

  await testIntegration();

  printSummary();

  // Exit with error code if tests failed
  process.exit(results.failed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(error => {
  log(`\nFatal error: ${error.message}`, 'red');
  process.exit(1);
});
