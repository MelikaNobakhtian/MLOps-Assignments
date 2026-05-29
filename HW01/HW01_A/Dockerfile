FROM python:3.11-slim

WORKDIR /app

# Copy only what's needed to install the package
COPY requirements.txt .
COPY pyproject.toml .
COPY src/ src/

# Install dependencies and the package
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Default command
CMD ["airbnb-ops", "run"]