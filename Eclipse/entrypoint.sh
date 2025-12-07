#!/bin/sh

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis started"

# Run migrations
python manage.py migrate --no-input

# Create default superuser if none exists
python manage.py create_default_superuser

# Collect static files
python manage.py collectstatic --no-input

# Create default avatar directories if they don't exist
mkdir -p /usr/src/Eclipse/media/avatars/defaults
mkdir -p /usr/src/Eclipse/media/rooms/defaults
mkdir -p /usr/src/Eclipse/staticfiles/default_avatars

# Create simple placeholder images if they don't exist
if [ ! -f "/usr/src/Eclipse/media/avatars/defaults/account.png" ]; then
    # Create a simple user default avatar using Pillow (if available)
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (70, 130, 180))  # Steel Blue
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'USER', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/avatars/defaults/account.png')
print('Created default user avatar account.png')
"
    # If Pillow is not available, we'll handle it in the Django app
    echo "Created default user avatar account.png"
fi

if [ ! -f "/usr/src/Eclipse/media/avatars/defaults/account(1).png" ]; then
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (100, 149, 237))  # Cornflower Blue
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'USR1', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/avatars/defaults/account(1).png')
print('Created default user avatar account(1).png')
"
    echo "Created default user avatar account(1).png"
fi

if [ ! -f "/usr/src/Eclipse/media/avatars/defaults/account(2).png" ]; then
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (64, 224, 208))  # Turquoise
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'USR2', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/avatars/defaults/account(2).png')
print('Created default user avatar account(2).png')
"
    echo "Created default user avatar account(2).png"
fi

if [ ! -f "/usr/src/Eclipse/media/avatars/defaults/account(3).png" ]; then
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (255, 165, 0))  # Orange
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'USR3', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/avatars/defaults/account(3).png')
print('Created default user avatar account(3).png')
"
    echo "Created default user avatar account(3).png"
fi

if [ ! -f "/usr/src/Eclipse/media/avatars/defaults/account(4).png" ]; then
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (220, 20, 60))  # Crimson
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'USR4', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/avatars/defaults/account(4).png')
print('Created default user avatar account(4).png')
"
    echo "Created default user avatar account(4).png"
fi

if [ ! -f "/usr/src/Eclipse/media/avatars/defaults/account(5).png" ]; then
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (255, 20, 147))  # Deep Pink
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'USR5', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/avatars/defaults/account(5).png')
print('Created default user avatar account(5).png')
"
    echo "Created default user avatar account(5).png"
fi

if [ ! -f "/usr/src/Eclipse/media/rooms/defaults/room.png" ]; then
    # Create a simple room default avatar using Pillow (if available)
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (34, 139, 34))  # Forest Green
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'ROOM', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/rooms/defaults/room.png')
print('Created default room avatar room.png')
"
    # If Pillow is not available, we'll handle it in the Django app
    echo "Created default room avatar room.png"
fi

if [ ! -f "/usr/src/Eclipse/media/rooms/defaults/room(1).png" ]; then
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (255, 105, 180))  # Hot Pink
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'RM1', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/rooms/defaults/room(1).png')
print('Created default room avatar room(1).png')
"
    echo "Created default room avatar room(1).png"
fi

if [ ! -f "/usr/src/Eclipse/media/rooms/defaults/room(2).png" ]; then
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (255, 215, 0))  # Gold
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'RM2', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/rooms/defaults/room(2).png')
print('Created default room avatar room(2).png')
"
    echo "Created default room avatar room(2).png"
fi

if [ ! -f "/usr/src/Eclipse/media/rooms/defaults/room(3).png" ]; then
    python -c "
import os
from PIL import Image, ImageDraw
# Create a simple image
img = Image.new('RGB', (200, 200), (0, 255, 127))  # Spring Green
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 190, 190], outline=(255, 255, 255), width=3)
draw.text((80, 90), 'RM3', fill=(255, 255, 255))
img.save('/usr/src/Eclipse/media/rooms/defaults/room(3).png')
print('Created default room avatar room(3).png')
"
    echo "Created default room avatar room(3).png"
fi

# Start the application
exec "$@"