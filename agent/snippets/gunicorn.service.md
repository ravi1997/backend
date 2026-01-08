# Snippet: systemd gunicorn service (template)

```ini
[Unit]
Description=Gunicorn for Flask app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/myapp
EnvironmentFile=/srv/myapp/.env
ExecStart=/srv/myapp/.venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 "myapp:create_app()"
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
