# Stack Fingerprint: Python Flask

## Purpose

Identifies and configures the Agent for a Flask-based web service.

## Signals

- `from flask import Flask` in source files.
- `app.run()` or `flask run` commands.
- `requirements.txt` containing `Flask`.

## Configuration

- **Entrypoint**: `app.py` or `wsgi.py`.
- **Build Command**: `pip install -r requirements.txt`.
- **Test Command**: `pytest` or `python -m unittest`.
- **Style Rule**: PEP8.

## Procedure

1. Identify `app` instance.
2. Locate `templates` and `static` folders.
3. Check for ORM (Flask-SQLAlchemy) or other plugins.
