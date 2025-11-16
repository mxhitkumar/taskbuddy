#!/bin/bash
# Setup script for Service Marketplace Platform

echo "🚀 Setting up Service Marketplace Platform..."

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Create media directories
echo "📁 Creating media directories..."
mkdir -p media/avatars
mkdir -p media/services/thumbnails
mkdir -p media/services/images
mkdir -p media/verifications/id_proofs
mkdir -p media/verifications/licenses
mkdir -p media/verifications/certificates
mkdir -p media/bookings/attachments
mkdir -p media/reviews/images

# Create templates directory
echo "📁 Creating templates directory..."
mkdir -p templates/emails

# Create static directory
echo "📁 Creating static directories..."
mkdir -p static
mkdir -p staticfiles

# Set permissions
echo "🔐 Setting permissions..."
chmod -R 755 logs media templates static staticfiles

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from example..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your configuration"
fi

echo "✅ Directory structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: python manage.py migrate"
echo "3. Run: python manage.py createsuperuser"
echo "4. Run: python manage.py runserver"
echo ""
echo "Happy coding! 🎉"