# Snippet: logrotate (template)

```conf
/var/log/nginx/*.log /var/log/myapp/*.log {
  daily
  rotate 14
  compress
  delaycompress
  missingok
  notifempty
  copytruncate
}
```
