# The MCP gateway ships in the SignalWire SDK as the mcp-gateway command.
# This image installs the SDK and runs that command.
FROM python:3.12-slim

WORKDIR /app

# curl for the health check
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Pin an SDK release with --build-arg SDK_VERSION=x.y.z
ARG SDK_VERSION=""
RUN pip install --no-cache-dir \
    "signalwire-sdk[mcp-gateway]${SDK_VERSION:+==${SDK_VERSION}}"

# The sample configuration, and the test MCP server it runs
COPY sample_config.json ./
COPY test/ ./test/

RUN mkdir -p certs sandbox

EXPOSE 8080

# Without a config.json, mcp-gateway starts from sample_config.json.
# docker-compose.yml copies a config.json from the host directory first.
CMD ["mcp-gateway", "-c", "config.json"]
