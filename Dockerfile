# Official Python Slim Image compatible with Red Hat OpenShift
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . /app/

# Collect static assets into staticfiles/
RUN python manage.py collectstatic --noinput

# OpenShift Arbitrary UID / GID 0 Security Compliance
# OpenShift runs containers as a random UID in root group (GID 0)
RUN chgrp -R 0 /app && \
    chmod -R g=u /app && \
    chmod +x /app/entrypoint.sh

# Expose standard unprivileged container port for OpenShift
EXPOSE 8080

# Switch to non-root user (1001) for strict security
USER 1001

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3", "--timeout", "120"]
