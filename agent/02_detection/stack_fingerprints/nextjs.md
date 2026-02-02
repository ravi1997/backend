# Stack Fingerprint: Next.js

## Purpose

Identifies and configures for a Next.js (App or Pages Router) project.

## Signals

- `next` dependency.
- `next.config.js`.
- `app/` or `pages/` directory.

## Configuration

- **Framework**: Next.js.
- **Language**: TS or JS.
- **SSR**: Enabled by default.
- **API**: Built-in routes.

## Docker Baseline

- **Base Image**: `node:20-alpine`.
- **Multi-stage**: Builder for `npm install` + `next build`, runtime with standalone output.
- **User**: Run as non-root user (`USER node`).
- **Port**: Expose `3000`.
- **Optimization**: Use `output: 'standalone'` in `next.config.js` for minimal image.
- **Hot Reload**: Mount code in dev compose, use `next dev` command.

## GitHub Actions Baseline

- **Workflow**: `.github/workflows/ci.yml`.
- **Jobs**: lint (next lint), test (jest), build (next build + docker build).
- **Node Version**: `20.x` (LTS).
- **Caching**: Cache `.next/cache` and `node_modules`.
- **Preview Deploys**: Optional Vercel/Netlify integration on PRs.

## Recommended Gates

- `gate_react_prop_types.md` (if using React prop validation)
- `gate_global_docker.md`
- `gate_global_ci_github.md`
