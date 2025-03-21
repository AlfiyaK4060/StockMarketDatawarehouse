FROM python:3.12-alpine

WORKDIR /app

# Install PostgreSQL client libraries
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

# Create log file and ensure it has proper permissions
RUN mkdir -p /app/logs && touch /app/logs/api.log && chmod 666 /app/logs/api.log

# Copy the application code
COPY app/ .

# Expose port
EXPOSE 5000

# Set the log directory and expose the log file
CMD ["python", "-u", "app.py"]
