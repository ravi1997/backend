# Maintenance Mode Implementation Notes

## Goals
- One command to enable maintenance page for one or many apps
- Must be reversible quickly

## Nginx approach
- Use `map` or `include` file toggle:
  - `include /etc/nginx/maintenance/<app>.conf;`
- Maintenance conf returns static HTML for all routes except health endpoints.

## App approach
- Flask middleware to short-circuit requests when MAINTENANCE=1
- Keep `/healthz` returning 200 for infra checks (or configurable)

## One-command toggle
- `ln -sf /etc/nginx/maintenance/<app>.on.conf /etc/nginx/maintenance/<app>.conf && nginx -s reload`
- Off: link to `.off.conf` and reload

## Verification
- curl returns maintenance page
- health endpoints still ok (if desired)
