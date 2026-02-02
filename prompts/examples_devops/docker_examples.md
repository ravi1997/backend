# Docker Examples Collection

## 1. Python (Flask/FastAPI)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

## 2. Node (Express)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["node", "app.js"]
```

## 3. React Vite

```dockerfile
# Build Stage
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Run Stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

## 4. Flutter

```dockerfile
FROM cirrusci/flutter:stable
WORKDIR /app
COPY . .
RUN flutter pub get
RUN flutter build web
```

## 5. Java Spring

```dockerfile
FROM eclipse-temurin:17-jdk-alpine
VOLUME /tmp
COPY target/*.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]
```

## 6. C++ CMake

```dockerfile
FROM gcc:latest
WORKDIR /app
COPY . .
RUN mkdir build && cd build && cmake .. && make
CMD ["./build/myapp"]
```
