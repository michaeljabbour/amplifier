# Terminal-Bench Recursive Reasoning Evaluation Environment
# Multi-stage build for optimized image size

# Stage 1: Python base with all dependencies
FROM python:3.12-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    docker.io \
    docker-compose \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Stage 2: Development/Evaluation environment
FROM base as evaluation

# Copy the entire repository
COPY . /app/

# Create results directory
RUN mkdir -p /app/results

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DOCKER_HOST=tcp://docker:2375

# Default command runs evaluation
CMD ["uv", "run", "run_full_evaluation.py", "--split", "small"]

# Stage 3: Agent runner (isolated environment for each task)
FROM base as agent-runner

# Copy only necessary files for agent execution
COPY custom_agents.py /app/
COPY tasks/ /app/tasks/
COPY utils/ /app/utils/

# Set working directory for task execution
WORKDIR /app/workspace

# This stage will be used by docker-compose for parallel task execution
CMD ["python", "-c", "print('Agent runner container ready')"]