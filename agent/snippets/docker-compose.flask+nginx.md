# Snippet: docker-compose (flask + nginx) minimal

```yaml
services:
  web:
    build: .
    environment:
      - APP_ENV=staging
    expose:
      - "8000"
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - web
```
