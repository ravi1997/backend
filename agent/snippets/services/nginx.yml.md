# Snippet: Nginx Reverse Proxy Service

```yaml
  nginx:
    image: nginx:1.25-alpine
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
    networks:
      - app_network
```

## Note

Requires a local file named `nginx.conf` relative to the docker-compose.yml.
