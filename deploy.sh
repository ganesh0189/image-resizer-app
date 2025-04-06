#!/bin/bash

# Deploy script for Image Resizer App

echo "🚀 Deploying Image Resizer App to GitHub..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git and try again."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Initializing git repository..."
    git init
fi

# Add all files to git
echo "📦 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Update: Image Resizer App with compression and step-by-step flow"

# Add remote if it doesn't exist
if ! git remote | grep -q "origin"; then
    echo "🔗 Adding remote repository..."
    git remote add origin https://github.com/ganesh0189/image-resizer-app.git
fi

# Push to GitHub
echo "⬆️ Pushing to GitHub..."
git push -u origin main

echo "✅ Deployment complete!"
echo "🌐 Your application is now available at: https://github.com/ganesh0189/image-resizer-app"
echo "🚀 Render will automatically deploy your application from GitHub." 