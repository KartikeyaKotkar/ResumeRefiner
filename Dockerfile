# Use slim image to keep the final container size small
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logging for Docker logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies (gcc is often required for compiled Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements first to leverage Docker's layer caching for faster builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Run as a non-privileged user to minimize security risks
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Execute the application entry point
CMD ["python", "main.py"]