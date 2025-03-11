FROM python:3.12-alpine

WORKDIR /app

# Install PostgreSQL client libraries
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

COPY app/ .

EXPOSE 5000

CMD ["python", "-u", "app.py"]