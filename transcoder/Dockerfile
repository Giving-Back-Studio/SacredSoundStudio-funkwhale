FROM alpine:latest

# Install required packages
RUN apk update && \
    apk add --no-cache \
    ffmpeg \
    python3 \
    py3-pip \
    && pip3 install --no-cache-dir awscli

# Create working directory
WORKDIR /app

# Copy transcode script
COPY transcode.sh /app/
RUN chmod +x /app/transcode.sh

# Environment variables for AWS configuration
ENV AWS_DEFAULT_REGION=us-east-1
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""

ENTRYPOINT ["/app/transcode.sh"]
