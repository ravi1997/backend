# Flask Diagnostics Bundle

- Environment: `echo $FLASK_APP $FLASK_ENV`; `python -c "import flask; print(flask.__version__)"`.
- App factory: inspect wsgi.py/app.py for `create_app`; run `flask routes`.
- Config dump (safe): run shell with `flask shell -c 'import pprint; from app import create_app; app=create_app(); pprint.pp({k:v for k,v in app.config.items() if k in ["ENV","DEBUG","TESTING","PREFERRED_URL_SCHEME"]})'`.
- Blueprints: `flask routes` to ensure endpoints registered; `python -X importtime` for import cycles.
- Database: `flask db current`, `flask db heads`, `flask db upgrade --sql` dry run; test connection via psql/mysql client if available.
- Proxy/headers: curl through proxy to check forwarded headers and security headers; `gunicorn --check-config gunicorn.conf.py` if used.
- Logging/security: inspect headers via `curl -I http://localhost:5000/health`; look for HSTS/X-Content-Type-Options/X-Frame-Options.
