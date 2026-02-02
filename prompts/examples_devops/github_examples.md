# GitHub Actions Examples

## 1. Node.js CI

```yaml
name: Node CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 18
    - run: npm ci
    - run: npm test
```

## 2. Python CI

```yaml
name: Python CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    - run: pip install -r requirements.txt
    - run: pytest
```

## 3. Deployment (Generic)

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy Script
        run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
```
