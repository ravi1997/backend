# Snippet: Flutter Web Dockerfile (Multi-stage)

```dockerfile
# Stage 1: Build
FROM ghcr.io/cirruslabs/flutter:stable AS builder

WORKDIR /app
COPY . .

# Release build
RUN flutter build web --release

# Stage 2: Serve
FROM nginx:1.25-alpine

# Copy built assets to Nginx html folder
COPY --from=builder /app/build/web /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
```
