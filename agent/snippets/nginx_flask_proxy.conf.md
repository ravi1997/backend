# Snippet: Nginx → Flask (gunicorn) proxy (template)

> Adapt paths/ports. Keep request-id propagation.

```nginx
location / {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Request ID propagation
    proxy_set_header X-Request-ID $request_id;
    add_header X-Request-ID $request_id;

    proxy_connect_timeout 10s;
    proxy_read_timeout 120s;

    proxy_pass http://127.0.0.1:8000;
}
```
