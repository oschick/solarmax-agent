#!/bin/bash
# Release script for solarmax-agent
# Usage: ./release.sh 1.0.0

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.0"
    exit 1
fi

# Validate version format
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Version must be in format X.Y.Z"
    exit 1
fi

echo "🚀 Creating release v$VERSION"

# Update config.json
echo "📝 Updating config.json..."
sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" config.json
rm config.json.bak

# Check if there are any changes and commit if needed
if git diff --quiet config.json; then
    echo "⚠️  Version is already $VERSION in config.json"
else
    echo "✅ Updated version to $VERSION"
    git add config.json
    git commit -m "chore: bump version to $VERSION"
fi

# Check if tag already exists
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "⚠️  Tag v$VERSION already exists"
    echo "📋 You can create a GitHub release manually at:"
    echo "   https://github.com/oschick/solarmax-agent/releases/new"
    echo "   Tag: v$VERSION"
    echo "   Title: Release v$VERSION"
else
    # Create and push tag
    echo "🏷️  Creating tag..."
    git tag "v$VERSION"
    git push origin master
    git push origin "v$VERSION"
    echo "✅ Release v$VERSION created!"
fi
echo "🔗 Check GitHub Actions for build progress"
echo "📦 Docker images and HA addon will be updated automatically"
