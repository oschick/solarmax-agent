FROM python:3.13-slim

# Create non-root user for security
RUN addgroup --gid 1337 app && adduser --uid 1337 --gid 1337 --disabled-password --gecos "App User" app

# Copy application files
COPY ./src/python /app
COPY ./requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Set ownership and switch to non-root user
RUN chown -R app:app /app
USER 1337:1337

WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('${INVERTER_IP}', ${INVERTER_PORT:-12345})); s.close()" || exit 1

# Run the application
CMD ["python", "-u", "agent.py"]
