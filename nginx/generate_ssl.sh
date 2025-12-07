#!/bin/sh

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/nginx.key \
    -out ssl/nginx.crt \
    -subj "/C=US/ST=California/L=San Francisco/O=Eclipse/OU=Development/CN=localhost"

echo "Self-signed SSL certificate generated in nginx/ssl/"
