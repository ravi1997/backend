# GitHub Action Template: CI Pipeline

```yaml
name: CI

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main", "develop" ]

jobs:
  # Job 1: Build & Test
  build-and-test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
        # python-version: [3.11] for python

    steps:
    - uses: actions/checkout@v3

    # Setup (Node Example)
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    # Dependencies
    - name: Install Dependencies
      run: npm ci

    # Lint
    - name: Lint
      run: npm run lint

    # Test
    - name: Test
      run: npm test

    # Build
    - name: Build
      run: npm run build

  # Job 2: Security Scan
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner in repo mode
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          ignore-unfixed: true
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'

  # Job 3: Docker Build (Verify Dockerfile)
  docker:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build . --file Dockerfile --tag myapp:${{ github.sha }}
```
