# Snippet: MongoDB Compose Service

```yaml
  mongo:
    image: mongo:7.0-jammy
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER:-root}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD:-example}
    volumes:
      - mongo_data:/data/db
    networks:
      - app_network
```

## Volumes Check

Ensure you add this to your `volumes:` block:

```yaml
volumes:
  mongo_data:
```
