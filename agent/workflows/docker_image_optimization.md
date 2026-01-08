# WORKFLOW: Docker Image Optimization

**Purpose:** Reduce image size and improve build performance.
**Source:** `workflows/docker_image_optimization.md`

## 1. Analysis
1. **Size check:** `docker images` to see current size.
2. **Layer analysis:** Use `docker history <image>` or tools like `dive` to find large layers.
3. **Common culprits:** Large build dependencies, caches (apt/npm), or uncompressed assets.

## 2. Implementation Steps
- [ ] **Use Multistage Builds:**
  ```dockerfile
  # Build stage
  FROM node:18 AS builder
  WORKDIR /app
  COPY . .
  RUN npm install && npm run build
  
  # Final stage
  FROM nginx:alpine
  COPY --from=builder /app/dist /usr/share/nginx/html
  ```
- [ ] **Consolidate RUN commands:** Minimize layers by combining commands.
- [ ] **Clean up caches:** `RUN apt-get update && apt-get install -y ... && rm -rf /var/lib/apt/lists/*`.
- [ ] **Use `.dockerignore`:** Exclude `node_modules`, `.git`, and build artifacts from the build context.

## 3. Layer Caching
- [ ] **Copy order:** Copy `package.json` or `pom.xml` BEFORE copying source code to leverage cache for dependency installation.

## 4. Verification
- [ ] Compare image size before and after.
- [ ] Verify build time with/without cache.
- [ ] Ensure application still functions correctly.

## 5. Artifacts
- **Output:** Optimization notes in `artifacts/DECISION_RECORD.md`.
