#!/bin/bash

# Function to prompt for user input with a default value
prompt_for_input() {
    local prompt_text=$1
    local default_value=$2
    local user_input
    read -p "$prompt_text [$default_value]: " user_input
    echo "${user_input:-$default_value}"
}

# --- Welcome Message ---
echo "========================================"
echo " Eclipse Interactive Installer"
echo "========================================"
echo "This script will guide you through the setup process."
echo

# --- Database Credentials ---
echo "--- Database Setup ---"
db_user=$(prompt_for_input "Enter database username" "devuser")
db_password=$(prompt_for_input "Enter database password" "devpass")
echo

# --- Superuser Credentials ---
echo "--- Django Superuser Setup ---"
su_username=$(prompt_for_input "Enter admin username" "admin")
su_password=$(prompt_for_input "Enter admin password" "admin123")
su_email=$(prompt_for_input "Enter admin email" "admin@example.com")
echo

# --- Generate Secret Key ---
echo "Generating a new Django SECRET_KEY..."
# Use openssl to generate a random key
secret_key=$(openssl rand -base64 48)
echo

# --- Create .env.db.dev ---
echo "Creating .env.db.dev..."
cat > .env.db.dev <<EOL
# PostgreSQL settings for development
POSTGRES_DB=eclipsedev
POSTGRES_USER=${db_user}
POSTGRES_PASSWORD=${db_password}
POSTGRES_HOST=db
POSTGRES_PORT=5432
EOL

# --- Create .env.db.prod ---
echo "Creating .env.db.prod..."
cat > .env.db.prod <<EOL
# PostgreSQL settings for production
POSTGRES_DB=eclipseprod
POSTGRES_USER=produser
POSTGRES_PASSWORD=change_me_to_a_strong_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
EOL

# --- Create Eclipse/.env.dev ---
echo "Creating Eclipse/.env.dev..."
cat > Eclipse/.env.dev <<EOL
# Django settings for development
SECRET_KEY=${secret_key}
DEBUG=True

# Default superuser credentials for development
DEFAULT_SUPERUSER_USERNAME=${su_username}
DEFAULT_SUPERUSER_EMAIL=${su_email}
DEFAULT_SUPERUSER_PASSWORD=${su_password}
EOL

# --- Create Eclipse/.env.prod ---
echo "Creating Eclipse/.env.prod..."
cat > Eclipse/.env.prod <<EOL
# Django settings for production
SECRET_KEY=change_me_to_a_long_random_string_for_production
DEBUG=False

# Default superuser credentials (not recommended for production)
DEFAULT_SUPERUSER_USERNAME=${su_username}
DEFAULT_SUPERUSER_EMAIL=${su_email}
DEFAULT_SUPERUSER_PASSWORD=${su_password}
EOL

echo ".env files created successfully."
echo

# --- Generate SSL Certificates ---
echo "--- SSL Certificate Generation ---"
if [ -f "nginx/generate_ssl.sh" ]; then
    echo "Running script to generate self-signed SSL certificates..."
    cd nginx
    ./generate_ssl.sh
    cd ..
    echo
else
    echo "Warning: nginx/generate_ssl.sh not found. Skipping SSL certificate generation."
    echo
fi

# --- Final Instructions ---
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo
echo "You can now build and run the application using Docker:"
echo "  docker-compose -f docker-compose.dev.yml up --build"
echo
echo "The application will be available at https://localhost:1338"
echo
