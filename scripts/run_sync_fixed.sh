#!/bin/bash
# Load Cloudinary secrets and run the FIXED sync script

set -e

echo "🔑 Setting up Cloudinary credentials..."

export CLOUDINARY_CLOUD_NAME="du0lumtob"

# Check if env vars are already set
if [ -z "$CLOUDINARY_API_KEY" ]; then
    echo "Enter your Cloudinary API Key:"
    read -s CLOUDINARY_API_KEY
    export CLOUDINARY_API_KEY
fi

if [ -z "$CLOUDINARY_API_SECRET" ]; then
    echo "Enter your Cloudinary API Secret:"
    read -s CLOUDINARY_API_SECRET
    export CLOUDINARY_API_SECRET
fi

if [ -z "$CLOUDINARY_API_KEY" ] || [ -z "$CLOUDINARY_API_SECRET" ]; then
    echo "❌ Missing Cloudinary credentials"
    exit 1
fi

echo "✅ Credentials loaded successfully"
echo ""

# Run the FIXED sync script
python3 scripts/sync_cloudinary_mapping_fixed.py
