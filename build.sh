#!/bin/bash

CONTROL_FILE="deb/DEBIAN/control"

# Get current version from DEBIAN/control
CURRENT_VERSION=$(grep '^Version:' "$CONTROL_FILE" | awk '{print $2}')
echo "Current version: $CURRENT_VERSION"

# Split version number into major and minor
IFS='.' read -r MAJOR MINOR <<< "$CURRENT_VERSION"

# Ask user if they want to increase major or minor version
echo "[m] Increase major version ($CURRENT_VERSION -> $((MAJOR + 1)).0)"
echo "[n] Increase minor version ($CURRENT_VERSION -> $MAJOR.$((MINOR + 1)))"
echo "Or press enter to keep current version"
read -p "[m/n]: " CHOICE

if [[ "$CHOICE" == "m" ]]; then
    MAJOR=$((MAJOR + 1))
    MINOR=0
elif [[ "$CHOICE" == "n" ]]; then
    MINOR=$((MINOR + 1))
fi

NEW_VERSION="$MAJOR.$MINOR"

# Update version number in DEBIAN/control if it has changed
if [[ "$NEW_VERSION" != "$CURRENT_VERSION" ]]; then
    echo "Updating version number to $NEW_VERSION"
    sed -i "s/^Version: .*/Version: $NEW_VERSION/" "$CONTROL_FILE"
fi

# Build binary with pyinstaller
pyinstaller --onefile --distpath deb/usr/local/bin/ --clean --name mqtt-commands mqtt-commands.py

# Build deb package
OUTPUT_FILE="dist/mqtt-commands-${NEW_VERSION}.deb"
dpkg-deb --build deb/ "$OUTPUT_FILE"

echo "Build complete. Created: $OUTPUT_FILE"
