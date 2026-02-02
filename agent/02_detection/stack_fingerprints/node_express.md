# Stack Fingerprint: Node Express

## Purpose

Identifies and configures for a Node.js Express server.

## Signals

- `express` in `package.json`.
- `const express = require('express')` or `import express from 'express'`.

## Configuration

- **Entrypoint**: `index.js`, `server.js`, or `src/app.ts`.
- **Run Command**: `npm start` or `node index.js`.
- **Style Rule**: ESLint (AirBnb or Standard).

## Docker Baseline

- **Base Image**: `node:20-alpine` or `node:20-slim`.
- **Multi-stage**: Use builder for `npm install`, runtime for execution.
- **User**: Run as non-root user (`USER node`).
- **Port**: Expose `3000` (common Express default).
- **Healthcheck**: `CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1`.
- **Hot Reload**: Mount `./src:/app/src` and use `nodemon` in dev compose.

## GitHub Actions Baseline

- **Workflow**: `.github/workflows/ci.yml`.
- **Jobs**: lint (eslint), test (jest/mocha), build (docker build).
- **Node Version Matrix**: Test on `[18.x, 20.x, 22.x]`.
- **Caching**: Cache `node_modules` using `actions/cache`.
- **Security**: Run `npm audit` in CI.

## Recommended Gates

- `gate_node_npm_audit.md`
- `gate_global_docker.md`
- `gate_global_ci_github.md`
