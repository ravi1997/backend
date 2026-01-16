# Snippet: Dockerfile for Node.js (Multi-stage)

```dockerfile

# Scope: Node.js (Express, NestJS, etc.)

# Metadata: multi-stage, non-root, alpine

# CLARIFY: node_version (e.g. 18-alpine)

# --- Build Stage ---

FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies

COPY package*.json ./

# Use 'npm ci' for deterministic builds

RUN npm ci

# Copy source and build (if TS/React build step exists)

COPY . .

# RUN npm run build # Uncomment if build step is needed

# --- Runtime Stage ---

FROM node:18-alpine

WORKDIR /app

# Create non-root user (alpine has 'node' user by default, but good to be explicit or use it)

# Alpine's 'node' user is usually uid 1000

ENV NODE_ENV=production

# Copy only necessary files

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app .

# If you have a dist/ folder from build, copy that instead of '.'

# COPY --from=builder /app/dist ./dist

# Switch to non-root user

USER node

EXPOSE 3000

CMD ["npm", "start"]

```
