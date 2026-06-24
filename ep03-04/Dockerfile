FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /app

# Copy dependency files first (Docker cache)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync

# Copy source code
COPY crawlers/ ./crawlers/
COPY *.py ./

ENV TZ=Asia/Taipei

CMD ["/bin/bash"]
