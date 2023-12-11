FROM python:3.11

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY app app

# Copy Alembic configurations and migration scripts
COPY alembic.ini .
COPY alembic alembic

# Copy the entrypoint script
COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

# Set the entrypoint script to be executed
ENTRYPOINT ["./entrypoint.sh"]
