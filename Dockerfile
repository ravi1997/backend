FROM python:3.12-slim

WORKDIR /app

# Copy the wheels from the host
COPY wheels /wheels

# Install the packages from the local wheels directory
RUN pip install --no-index --find-links=/wheels /wheels/*

# Copy the rest of the application
COPY . .

EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
