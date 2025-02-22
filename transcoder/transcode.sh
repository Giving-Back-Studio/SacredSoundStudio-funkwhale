#!/bin/sh

# Exit on any error
set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <s3_bucket> <s3_key>"
    exit 1
fi

S3_BUCKET=$1
S3_KEY=$2
FILENAME=$(basename "$S3_KEY" | sed 's/\.[^.]*$//')

# Create working directories
mkdir -p input output

# Download file from S3
echo "Downloading $S3_KEY from $S3_BUCKET..."
aws s3 cp "s3://${S3_BUCKET}/${S3_KEY}" "input/${FILENAME}.mp4"

INPUT_FILE="input/${FILENAME}.mp4"

# Transcode to different resolutions
# 1080p (1920x1080)
ffmpeg -i "$INPUT_FILE" \
    -c:v libx264 -preset medium \
    -b:v 5000k -maxrate 5350k -bufsize 7000k \
    -vf "scale=1920:1080" \
    -c:a aac -b:a 192k \
    "output/${FILENAME}_1080p.mp4"

# 720p (1280x720)
ffmpeg -i "$INPUT_FILE" \
    -c:v libx264 -preset medium \
    -b:v 2800k -maxrate 2996k -bufsize 4200k \
    -vf "scale=1280:720" \
    -c:a aac -b:a 128k \
    "output/${FILENAME}_720p.mp4"

# 480p (854x480)
ffmpeg -i "$INPUT_FILE" \
    -c:v libx264 -preset medium \
    -b:v 1400k -maxrate 1498k -bufsize 2100k \
    -vf "scale=854:480" \
    -c:a aac -b:a 96k \
    "output/${FILENAME}_480p.mp4"

# 360p (640x360)
ffmpeg -i "$INPUT_FILE" \
    -c:v libx264 -preset medium \
    -b:v 800k -maxrate 856k -bufsize 1200k \
    -vf "scale=640:360" \
    -c:a aac -b:a 96k \
    "output/${FILENAME}_360p.mp4"

# Upload transcoded files back to S3
echo "Uploading transcoded files to S3..."
aws s3 sync output/ "s3://${S3_BUCKET}/transcoded/${FILENAME}/"

# Clean up
echo "Cleaning up local files..."
rm -rf input output

echo "Transcoding complete. Files uploaded to s3://${S3_BUCKET}/transcoded/${FILENAME}/"
