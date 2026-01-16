# Snippet: Redis Compose Service

```yaml
  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Volumes Check

Ensure you add this to your `volumes:` block:

```yaml
volumes:
  redis_data:
```
