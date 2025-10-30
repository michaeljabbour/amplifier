FROM python:3.10-slim

WORKDIR /app

# Install pytest for testing
RUN pip install pytest

# Copy solution script
COPY solution.sh /app/solution.sh
RUN chmod +x /app/solution.sh

# Copy tests
COPY tests /app/tests
