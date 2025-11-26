FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# Create config directory
RUN mkdir -p /app/config

ENV CONFIG_DIR=/app/config
ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["python", "app.py"]
