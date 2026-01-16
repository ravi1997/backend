# Snippet: C++ Dockerfile (CMake)

```dockerfile
# Build Stage
FROM ubuntu:22.04 AS builder

# Install build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Build
RUN mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc)

# Runtime Stage
FROM ubuntu:22.04-slim

WORKDIR /app

# Copy generic binary (adjust name 'my_app' as needed)
COPY --from=builder /app/build/my_app /app/my_app

# Runtime dependencies?
# RUN apt-get update && apt-get install -y libssl3 ...

EXPOSE 8080
CMD ["./my_app"]
```
